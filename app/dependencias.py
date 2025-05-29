# app/dependencias.py

from sqlalchemy.orm import Session
from fastapi import Depends
from app.base_de_datos import SesionLocal

def get_db():
    db = SesionLocal()
    try:
        yield db
    finally:
        db.close()
