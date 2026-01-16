from fastapi import FastAPI, Form
from fastapi.responses import JSONResponse
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import requests
from bs4 import BeautifulSoup

# -----------------------------
# Configuració base de dades
# -----------------------------
DATABASE_URL = "sqlite:///./ofertes.db"  # Si Render després vols PostgreSQL, només canvia l'URL

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Oferta(Base):
    __tablename__ = "ofertes"
    id = Column(Integer, primary_key=True, index=True)
    servei = Column(String)
    url_pdf = Column(String, unique=True, index=True)
    data_detectada = Column(DateTime, default=datetime.now)
    aplicada = Column(Boolean, default=False)

Base.metadata.create_all(bind=engine)

# -----------------------------
# Inicialització FastAPI
# -----------------------------
app = FastAPI()

# -----------------------------
# Funció de scraping
# -----------------------------
@app.get("/scrape")
def scrape():
    db = SessionLocal()
    try:
        # Exemple scraping dummy
        url = "http://www.idescat.cat/cat/idescat/publicacions/cataleg/pdfdocs/ecpci2007-08.pdf"
        servei = "Baix Llobregat"

        # Comprovar si ja existeix
        existing = db.query(Oferta).filter(Oferta.url_pdf == url).first()
        if existing:
            return JSONResponse({"message": "PDF ja existeix a la base de dades"}, status_code=200)

        nova_oferta = Oferta(
            servei=servei,
            url_pdf=url,
            data_detectada=datetime.now(),
            aplicada=False
        )
        db.add(nova_oferta)
        db.commit()
        return {"message": "Oferta afegida correctament", "url_pdf": url}
    except Exception as e:
        db.rollback()
        return JSONResponse({"error": str(e)}, status_code=500)
    finally:
        db.close()

# -----------------------------
# Endpoint per marcar com aplicada
# -----------------------------
@app.post("/aplicada")
def aplicada(id: int = Form(...)):
    db = SessionLocal()
    try:
        oferta = db.query(Oferta).filter(Oferta.id == id).first()
        if not oferta:
            return JSONResponse({"error": "Oferta no trobada"}, status_code=404)
        oferta.aplicada = True
        db.commit()
        return {"message": f"Oferta {id} marcada com aplicada"}
    except Exception as e:
        db.rollback()
        return JSONResponse({"error": str(e)}, status_code=500)
    finally:
        db.close()

