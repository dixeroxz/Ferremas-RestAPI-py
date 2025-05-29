from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.dependencias import get_db
from datetime import datetime
from app.repositorios.compra_repositorio import CompraRepositorio
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
