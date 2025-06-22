from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.base_de_datos import Base

class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    correo = Column(String(100), unique=True, nullable=False)
    contrasena = Column(String(255), nullable=False)
    direccion = Column(String(200), nullable=True)
    telefono = Column(String(20), nullable=True)
    rol = Column(String(20), default="cliente")

    compras = relationship("Compra", back_populates="usuario", cascade="all, delete-orphan")
    pagos = relationship("Pago", back_populates="usuario", cascade="all, delete-orphan")
