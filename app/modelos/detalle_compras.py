from sqlalchemy import Column, Integer, Float, ForeignKey, String
from sqlalchemy.orm import relationship
from app.base_de_datos import Base

class DetalleCompras(Base):
    __tablename__ = "detalle_compras"

    id = Column(Integer, primary_key=True, index=True)
    compra_id = Column(Integer, ForeignKey("compras.id"), nullable=False)
    producto_codigo = Column(String(20), ForeignKey("productos.codigo"), nullable=False)
    cantidad = Column(Integer, nullable=False)
    precio_unitario = Column(Float, nullable=False)

    compra = relationship("Compra", back_populates="detalles")
    producto = relationship("Producto")  
