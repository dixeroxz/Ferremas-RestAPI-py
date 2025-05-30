from sqlalchemy import Column, Integer, String, Float, DateTime, Enum, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum as PyEnum
from app.base_de_datos import Base

class Pago(Base):
    __tablename__ = "pagos"

    id = Column(Integer, primary_key=True, index=True)
    monto = Column(Float, nullable=False)
    moneda = Column(String(10), nullable=False, default="CLP")
    fecha_creacion = Column(DateTime, default=datetime.utcnow, nullable=False)
    fecha_actualizacion = Column(DateTime, default=datetime.utcnow, nullable=False)
    token = Column(String(200), nullable=True)
    url_redireccion = Column(String(300), nullable=True)

    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    usuario = relationship("Usuario", back_populates="pagos")

    compra_id = Column(Integer, ForeignKey("compras.id"), nullable=False, unique=True)
    compra = relationship("Compra", back_populates="pago")

