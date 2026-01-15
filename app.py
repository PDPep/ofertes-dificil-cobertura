from fastapi import FastAPI, Request, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean
from sqlalchemy.orm import sessionmaker, declarative_base
from datetime import datetime
import requests
from bs4 import BeautifulSoup

app = FastAPI()
templates = Jinja2Templates(directory="templates")

DATABASE_URL = "sqlite:///./ofertes.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

class Oferta(Base):
    __tablename__ = "ofertes"
    id = Column(Integer, primary_key=True)
    servei = Column(String)
    url_pdf = Column(String, unique=True)
    data_detectada = Column(DateTime, default=datetime.utcnow)
    aplicada = Column(Boolean, default=False)

Base.metadata.create_all(bind=engine)

SERVEIS = {
    "Catalunya Central": "https://educacio.gencat.cat/ca/departament/serveis-territorials/catalunya-central/personal-docent/nomenaments-telematics/dificil-cobertura/",
    "Baix Llobregat": "https://educacio.gencat.cat/ca/departament/serveis-territorials/baix-llobregat/personal-docent/nomenaments-telematics/dificil-cobertura/",
    "Girona": "https://educacio.gencat.cat/ca/departament/serveis-territorials/girona/personal-docent/nomenaments-telematics/dificil-cobertura/",
    "Barcelona Comarques": "https://educacio.gencat.cat/ca/departament/serveis-territorials/barcelona-comarques/personal-docent/nomenaments-telematics/dificil-cobertura/",
    "Vallès Occidental": "https://educacio.gencat.cat/ca/departament/serveis-territorials/valles-occidental/personal-docent/nomenaments-telematics/dificil-cobertura/",
    "Maresme–Vallès Oriental": "https://educacio.gencat.cat/ca/departament/serveis-territorials/maresme-valles-oriental/personal-docent/nomenaments-telematics/dificil-cobertura/",
    "Consorci BCN": "https://www.edubcn.cat/ca/professorat_i_pas/seleccio_rrhh/dificil_cobertura"
}

@app.get("/")
def index(request: Request):
    db = SessionLocal()
    ofertes = db.query(Oferta).order_by(Oferta.data_detectada.desc()).all()
    db.close()
    return templates.TemplateResponse("index.html", {
        "request": request,
        "ofertes": ofertes
    })

@app.post("/aplicada")
def marcar(oferta_id: int = Form(...)):
    db = SessionLocal()
    oferta = db.query(Oferta).get(oferta_id)
    oferta.aplicada = not oferta.aplicada
    db.commit()
    db.close()
    return RedirectResponse("/", status_code=303)

@app.get("/scrape")
def scrape():
    db = SessionLocal()
    existents = {o.url_pdf for o in db.query(Oferta).all()}

    for servei, url in SERVEIS.items():
        try:
            html = requests.get(url, timeout=15).text
            soup = BeautifulSoup(html, "html.parser")
            for a in soup.find_all("a", href=True):
                if a["href"].lower().endswith(".pdf"):
                    pdf = a["href"]
                    if not pdf.startswith("http"):
                        pdf = url.rstrip("/") + "/" + pdf.lstrip("/")
                    if pdf not in existents:
                        db.add(Oferta(servei=servei, url_pdf=pdf))
        except:
            pass

    db.commit()
    db.close()
    return {"ok": True}
