from sqlalchemy import Column, Integer, String, Float, DateTime, Enum
from datetime import datetime
from enum import Enum as PyEnum
from app.base_de_datos import Base

class EstadoPago(PyEnum):
    PENDIENTE = "PENDIENTE"
    APROBADO = "APROBADO"
    RECHAZADO = "RECHAZADO"
    ANULADO = "ANULADO"

class Pago(Base):
    __tablename__ = "pagos"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(String(100), unique=True, nullable=False)
    monto = Column(Float, nullable=False)
    moneda = Column(String(10), nullable=False, default="CLP")
    estado = Column(Enum(EstadoPago), default=EstadoPago.PENDIENTE, nullable=False)
    fecha_creacion = Column(DateTime, default=datetime.utcnow, nullable=False)
    fecha_actualizacion = Column(DateTime, default=datetime.utcnow, nullable=False)
    token = Column(String(200), nullable=True)       # token de transacción Webpay
    url_redireccion = Column(String(300), nullable=True)  # URL de pago para el cliente
