from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional, Generator
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from datetime import datetime

from app.base_de_datos import SesionLocal
from app.repositorios.producto_repositorio import ProductoRepositorio
from app.servicios.producto_servicio import ProductoServicio
from app.seguridad import validar_api_key_general, validar_api_key_interna

router = APIRouter()

def obtener_sesion() -> Generator[Session, None, None]:
    db = SesionLocal()
    try:
        yield db
    finally:
        db.close()

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
    categoria: str
    nombre: str
    stock: int
    precio: float
    historial_precios: List[PrecioSalida]
    class Config:
        from_attributes = True

class ProductoCrearEntrada(BaseModel):
    codigo: str = Field(..., example="FER-54321")
    marca: str = Field(..., example="Makita")
    nombre: str = Field(..., example="Sierra Circular Makita")
    categoria: str = Field(..., example="Herramientas Eléctricas")
    stock: int = Field(..., ge=0, example=15)
    precio: float = Field(..., gt=0, example=120000.50)


# --- Lectura: usa validar_api_key_general (heredado del include_router) ---
@router.get(
    "/{codigo}",
    response_model=ProductoDetalleSalida,
    summary="Obtener producto por código"
)
def obtener_por_codigo(
    codigo: str,
    servicio: ProductoServicio = Depends(obtener_servicio)
):
    producto, historial = servicio.obtener_detalle(codigo)
    return {
        "codigo": producto.codigo,
        "marca": producto.marca,
        "nombre": producto.nombre,
        "categoria":producto.categoria,
        "stock": producto.stock,
        "precio": producto.precio,
        "historial_precios": historial
    }

@router.get(
    "/",
    response_model=List[ProductoDetalleSalida],
    summary="Listar productos (filtro opcional por nombre)"
)
def listar_productos(
    nombre: Optional[str] = None,
    servicio: ProductoServicio = Depends(obtener_servicio)
):
    datos = servicio.listar(nombre)
    return [
        {
            "codigo": p.codigo,
            "marca": p.marca,
            "nombre": p.nombre,
            "categoria": p.categoria,
            "stock": p.stock,
            "precio": p.precio,
            "historial_precios": h
        }
        for p, h in datos
    ]

@router.get(
    "/categoria/{categoria}",
    response_model=List[ProductoDetalleSalida],
    summary="Listar por categoría"
)
def productos_por_categoria(
    categoria: str,
    servicio: ProductoServicio = Depends(obtener_servicio)
):
    datos = servicio.listar_por_categoria(categoria)
    return [
        {
            "codigo": p.codigo,
            "marca": p.marca,
            "nombre": p.nombre,
            "categoria": p.categoria,
            "stock": p.stock,
            "precio": p.precio,
            "historial_precios": h
        }
        for p, h in datos
    ]

@router.get(
    "/stock/bajo",
    response_model=List[ProductoDetalleSalida],
    summary="Listar stock bajo"
)
def productos_stock_bajo(
    umbral: int,
    servicio: ProductoServicio = Depends(obtener_servicio)
):
    datos = servicio.listar_stock_bajo(umbral)
    return [
        {
            "codigo": p.codigo,
            "marca": p.marca,
            "nombre": p.nombre,
            "categoria": p.categoria,
            "stock": p.stock,
            "precio": p.precio,
            "historial_precios": h
        }
        for p, h in datos
    ]


# --- Escritura: protege con validar_api_key_interna ---
@router.post(
    "/",
    response_model=ProductoDetalleSalida,
    status_code=status.HTTP_201_CREATED,
    summary="Crear un nuevo producto",
    dependencies=[Depends(validar_api_key_interna)]
)
def crear_producto(
    entrada: ProductoCrearEntrada,
    servicio: ProductoServicio = Depends(obtener_servicio)
):
    producto, historial = servicio.crear_producto(
        entrada.codigo,
        entrada.marca,
        entrada.nombre,
        entrada.categoria,
        entrada.stock,
        entrada.precio
    )
    return {
        "codigo": producto.codigo,
        "marca": producto.marca,
        "nombre": producto.nombre,
        "categoria":producto.categoria,
        "stock": producto.stock,
        "precio": producto.precio,
        "historial_precios": historial
    }

@router.put(
    "/{codigo}/precio",
    response_model=ProductoDetalleSalida,
    summary="Actualizar precio e historial",
    dependencies=[Depends(validar_api_key_interna)]
)
def actualizar_precio(
    codigo: str,
    nuevo_valor: float,
    servicio: ProductoServicio = Depends(obtener_servicio)
):
    producto, historial = servicio.cambiar_precio(codigo, nuevo_valor)
    return {
        "codigo": producto.codigo,
        "marca": producto.marca,
        "nombre": producto.nombre,
        "categoria":producto.categoria,
        "stock": producto.stock,
        "precio": producto.precio,
        "historial_precios": historial
    }

@router.delete(
    "/{codigo}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar un producto",
    dependencies=[Depends(validar_api_key_interna)]
)
def eliminar_producto(
    codigo: str,
    servicio: ProductoServicio = Depends(obtener_servicio)
):
    """
    Elimina un producto y su historial.
    Responde 204 No Content si tuvo éxito, 404 si no existe.
    """
    servicio.borrar_producto(codigo)
    return None
