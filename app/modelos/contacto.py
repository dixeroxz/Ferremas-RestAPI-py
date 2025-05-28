from sqlalchemy import Column, Integer, String, DateTime, Text
from datetime import datetime
from app.base_de_datos import Base

class Contacto(Base):
    __tablename__ = "contacto"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    email = Column(String(100), nullable=False)
    asunto = Column(String(200), nullable=False)
    mensaje = Column(Text, nullable=False)
    fecha = Column(DateTime, default=datetime.utcnow, nullable=False)
