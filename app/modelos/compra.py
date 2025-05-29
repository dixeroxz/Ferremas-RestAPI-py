# app/modelos/compra.py
from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey, String
from sqlalchemy.orm import relationship
from datetime import datetime
from app.base_de_datos import Base

class Compra(Base):
    __tablename__ = "compras"

    id = Column(Integer, primary_key=True, index=True)
    total = Column(Float, nullable=False)
    fecha = Column(DateTime, default=datetime.utcnow)
    estado = Column(String(20), default="pendiente", nullable=False)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    usuario = relationship("Usuario", back_populates="compras")
    pago = relationship("Pago", back_populates="compra", uselist=False)
    detalles = relationship("DetalleCompras", back_populates="compra", cascade="all, delete-orphan")
