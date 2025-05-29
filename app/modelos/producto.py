from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey 
from datetime import datetime
from app.base_de_datos import Base

class Producto(Base):
    __tablename__ = "productos"

    id = Column(Integer, primary_key=True, index=True)
    codigo = Column(String(50), unique=True, index=True, nullable=False)
    marca = Column(String(50), nullable=False)
    nombre = Column(String(100), nullable=False)
    categoria = Column(String(100), index=True, nullable=False)
    stock = Column(Integer, default=0, nullable=False)
    precio = Column(Float, default=0.0, nullable=False)   # ← precio vigente

class HistorialPrecio(Base):
    __tablename__ = "historial_precios"

    id = Column(Integer, primary_key=True, index=True)
    producto_id = Column(Integer, ForeignKey("productos.id"), nullable=False)
    fecha = Column(DateTime, default=datetime.utcnow)
    valor = Column(Float, nullable=False)
