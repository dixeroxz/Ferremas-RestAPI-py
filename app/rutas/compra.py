from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.dependencias import get_db
from datetime import datetime
from app.repositorios.compra_repositorio import CompraRepositorio
from app.servicios.compra_servicio import CompraServicio
from typing import List
from pydantic import BaseModel

  
router = APIRouter(prefix="/compras", tags=["Compras"])

  
# ======== Esquemas para entrada/salida ========

class ProductoCompra(BaseModel):
    codigo: str
    cantidad: int

class CompraCrear(BaseModel):
    usuario_id: int
    productos: List[ProductoCompra]
    total: float

class CompraRespuesta(BaseModel):
    id: int
    usuario_id: int
    total: float
    fecha: datetime
    estado: str
     
    class Config:
        orm_mode = True

class ProductoDetalle(BaseModel):
    codigo: str
    nombre: str
    precio: float
    cantidad: int
    subtotal: float
    
    class Config:
        orm_mode = True

class DetalleCompraRespuesta(BaseModel):
    producto_codigo: str
    cantidad: int
    precio_unitario: float
    subtotal: float
    producto: ProductoDetalle
    
    class Config:
        orm_mode = True

class CompraDetalladaRespuesta(BaseModel):
    id: int
    usuario_id: int
    total: float
    fecha: datetime
    estado: str
    detalles: List[DetalleCompraRespuesta] = []
    
    class Config:
        orm_mode = True

  
# ======== Endpoints de compras ========

@router.post("/", response_model=CompraRespuesta)
def crear_compra(data: CompraCrear, db: Session = Depends(get_db)):
    repo = CompraRepositorio(db)
    compra = repo.crear_compra_pendiente(
        usuario_id=data.usuario_id,
        productos=[p.dict() for p in data.productos],
        total=data.total
    )
    return compra

@router.delete("/{compra_id}", status_code=204)
def eliminar_compra(compra_id: int, db: Session = Depends(get_db)):
    repo = CompraRepositorio(db)
    success = repo.eliminar_compra(compra_id)
    if not success:
        raise HTTPException(status_code=404, detail="Compra no encontrada")
    return

@router.get("/{compra_id}", response_model=CompraRespuesta)
def obtener_compra(compra_id: int, db: Session = Depends(get_db)):
    repo = CompraRepositorio(db)
    compra = repo.obtener_compra(compra_id)
    if not compra:
        raise HTTPException(status_code=404, detail="Compra no encontrada")
    return compra

@router.get("/", response_model=List[CompraRespuesta])
def listar_compras(db: Session = Depends(get_db)):
    repo = CompraRepositorio(db)
    return repo.listar_compras()

@router.get("/usuario/{usuario_id}", response_model=List[CompraDetalladaRespuesta])
def listar_compras_usuario(usuario_id: int, db: Session = Depends(get_db)):
    """
    Lista todas las compras de un usuario específico con detalles ordenadas por fecha descendente
    """
    servicio = CompraServicio(db)
    compras = servicio.listar_compras_por_usuario(usuario_id)
    
    if not compras:
        raise HTTPException(
            status_code=404, 
            detail=f"No se encontraron compras para el usuario {usuario_id}"
        )
    
    # Procesamos cada compra para incluir los detalles
    compras_respuesta = []
    for compra in compras:
        detalles_procesados = []
        
        # Procesamos los detalles de cada compra
        for detalle in compra.detalles:
            producto_detalle = ProductoDetalle(
                codigo=detalle.producto.codigo,
                nombre=detalle.producto.nombre,
                precio=detalle.producto.precio,
                cantidad=detalle.cantidad,
                subtotal=detalle.cantidad * detalle.precio_unitario
            )
            
            detalle_respuesta = DetalleCompraRespuesta(
                producto_codigo=detalle.producto_codigo,
                cantidad=detalle.cantidad,
                precio_unitario=detalle.precio_unitario,
                subtotal=detalle.cantidad * detalle.precio_unitario,
                producto=producto_detalle
            )
            detalles_procesados.append(detalle_respuesta)
        
        # Creamos la respuesta completa para cada compra
        compra_respuesta = CompraDetalladaRespuesta(
            id=compra.id,
            usuario_id=compra.usuario_id,
            total=compra.total,
            fecha=compra.fecha,
            estado=compra.estado,
            detalles=detalles_procesados
        )
        compras_respuesta.append(compra_respuesta)
    
    return compras_respuesta

@router.get("/usuario/{usuario_id}/ultima", response_model=CompraDetalladaRespuesta)
def obtener_ultima_compra_usuario(usuario_id: int, db: Session = Depends(get_db)):
    """
    Obtiene la última compra de un usuario específico con todos los detalles
    """
    servicio = CompraServicio(db)
    compra = servicio.obtener_ultima_compra_usuario_con_detalles(usuario_id)
    
    if not compra:
        raise HTTPException(
            status_code=404, 
            detail=f"No se encontraron compras para el usuario {usuario_id}"
        )
    
    # Procesamos los detalles para incluir el subtotal
    detalles_procesados = []
    for detalle in compra.detalles:
        producto_detalle = ProductoDetalle(
            codigo=detalle.producto.codigo,
            nombre=detalle.producto.nombre,
            precio=detalle.producto.precio,
            cantidad=detalle.cantidad,
            subtotal=detalle.cantidad * detalle.precio_unitario
        )
        
        detalle_respuesta = DetalleCompraRespuesta(
            producto_codigo=detalle.producto_codigo,
            cantidad=detalle.cantidad,
            precio_unitario=detalle.precio_unitario,
            subtotal=detalle.cantidad * detalle.precio_unitario,
            producto=producto_detalle
        )
        detalles_procesados.append(detalle_respuesta)
    
    # Creamos la respuesta completa
    compra_respuesta = CompraDetalladaRespuesta(
        id=compra.id,
        usuario_id=compra.usuario_id,
        total=compra.total,
        fecha=compra.fecha,
        estado=compra.estado,
        detalles=detalles_procesados
    )
    
    return compra_respuesta