from fastapi import APIRouter, Depends, status
from typing import List, Generator
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime

from app.base_de_datos import SesionLocal
from app.repositorios.contacto_repositorio import ContactoRepositorio
from app.servicios.contacto_servicio import ContactoServicio
from app.seguridad import validar_api_key_general, validar_api_key_interna

router = APIRouter(prefix="/contacto", tags=["Contacto"])

def obtener_sesion() -> Generator[Session, None, None]:
    db = SesionLocal()
    try:
        yield db
    finally:
        db.close()

def obtener_servicio(db: Session = Depends(obtener_sesion)) -> ContactoServicio:
    return ContactoServicio(ContactoRepositorio(db))


class ContactoCrearEntrada(BaseModel):
    nombre: str = Field(..., example="Juan Pérez")
    email: EmailStr = Field(..., example="juan@example.com")
    asunto: str = Field(..., example="Consulta de inventario")
    mensaje: str = Field(..., example="¿Tienen taladro Bosch disponible?")


class ContactoSalida(BaseModel):
    id: int
    nombre: str
    email: EmailStr
    asunto: str
    mensaje: str
    fecha: datetime

    class Config:
        from_attributes = True


@router.post(
    "/",
    response_model=ContactoSalida,
    status_code=status.HTTP_201_CREATED,
    summary="Enviar un mensaje de contacto",
    dependencies=[Depends(validar_api_key_general)]
)
def enviar_mensaje(
    entrada: ContactoCrearEntrada,
    servicio: ContactoServicio = Depends(obtener_servicio)
):
    mensaje = servicio.enviar_mensaje(
        entrada.nombre,
        entrada.email,
        entrada.asunto,
        entrada.mensaje
    )
    return mensaje


@router.get(
    "/",
    response_model=List[ContactoSalida],
    summary="Listar todos los mensajes (sólo interna)",
    dependencies=[Depends(validar_api_key_interna)]
)
def listar_mensajes(
    servicio: ContactoServicio = Depends(obtener_servicio)
):
    return servicio.listar_mensajes()
