from fastapi import APIRouter, Depends
from typing import List, Optional, Generator
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime

from app.base_de_datos import SesionLocal
from app.repositorios.producto_repositorio import ProductoRepositorio
from app.servicios.producto_servicio import ProductoServicio

router = APIRouter()

def obtener_sesion() -> Generator[Session, None, None]:
    sesion = SesionLocal()
    try:
        yield sesion
    finally:
        sesion.close()

def obtener_servicio(db: Session = Depends(obtener_sesion)) -> ProductoServicio:
    repo = ProductoRepositorio(db)
    return ProductoServicio(repo)

class PrecioSalida(BaseModel):
    fecha: datetime
    valor: float
    class Config:
        from_attributes = True

class ProductoDetalleSalida(BaseModel):
    codigo: str
    marca: str
    nombre: str
    historial_precios: List[PrecioSalida]
    class Config:
        from_attributes = True

@router.get("/{codigo}", response_model=ProductoDetalleSalida, summary="Obtener producto por código")
def obtener_por_codigo(codigo: str, servicio: ProductoServicio = Depends(obtener_servicio)):
    producto, historial = servicio.obtener_detalle(codigo)
    return {
        "codigo": producto.codigo,
        "marca": producto.marca,
        "nombre": producto.nombre,
        "historial_precios": historial
    }

@router.get("/", response_model=List[ProductoDetalleSalida], summary="Listar productos (filtro opcional por nombre)")
def listar_productos(nombre: Optional[str] = None, servicio: ProductoServicio = Depends(obtener_servicio)):
    datos = servicio.listar(nombre)
    return [
        {
            "codigo": p.codigo,
            "marca": p.marca,
            "nombre": p.nombre,
            "historial_precios": hist
        }
        for p, hist in datos
    ]

@router.get("/categoria/{categoria}", response_model=List[ProductoDetalleSalida], summary="Listar por categoría")
def productos_por_categoria(categoria: str, servicio: ProductoServicio = Depends(obtener_servicio)):
    datos = servicio.listar_por_categoria(categoria)
    return [
        {
            "codigo": p.codigo,
            "marca": p.marca,
            "nombre": p.nombre,
            "historial_precios": hist
        }
        for p, hist in datos
    ]

@router.get("/stock/bajo", response_model=List[ProductoDetalleSalida], summary="Listar stock bajo")
def productos_stock_bajo(umbral: int, servicio: ProductoServicio = Depends(obtener_servicio)):
    datos = servicio.listar_stock_bajo(umbral)
    return [
        {
            "codigo": p.codigo,
            "marca": p.marca,
            "nombre": p.nombre,
            "historial_precios": hist
        }
        for p, hist in datos
    ]

@router.put("/{codigo}/precio", response_model=ProductoDetalleSalida, summary="Actualizar precio e historial")
def actualizar_precio(codigo: str, nuevo_valor: float, servicio: ProductoServicio = Depends(obtener_servicio)):
    producto, historial = servicio.cambiar_precio(codigo, nuevo_valor)
    return {
        "codigo": producto.codigo,
        "marca": producto.marca,
        "nombre": producto.nombre,
        "historial_precios": historial
    }
