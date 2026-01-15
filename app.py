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

# Base de dades SQLite
DATABASE_URL = "sqlite:///./ofertes.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

# Model
class Oferta(Base):
    __tablename__ = "ofertes"
    id = Column(Integer, primary_key=True)
    servei = Column(String)
    url_pdf = Column(String, unique=True)
    data_detectada = Column(DateTime, default=datetime.utcnow)
    aplicada = Column(Boolean, default=False)

Base.metadata.create_all(bind=engine)

# Serveis territorials
SERVEIS = {
    "Catalunya Central": "https://educacio.gencat.cat/ca/departament/serveis-territorials/catalunya-central/personal-docent/nomenaments-telematics/dificil-cobertura/",
    "Baix Llobregat": "https://educacio.gencat.cat/ca/departament/serveis-territorials/baix-llobregat/personal-docent/nomenaments-telematics/dificil-cobertura/",
    "Girona": "https://educacio.gencat.cat/ca/departament/serveis-territorials/girona/per
