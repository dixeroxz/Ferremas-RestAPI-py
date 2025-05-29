from fastapi import APIRouter, Depends, Body
from sqlalchemy.orm import Session
from app.dependencias import get_db
from app.servicios.usuario_servicio import crear_usuario
from fastapi import HTTPException

router = APIRouter()

@router.post("/usuarios")
async def ruta_crear_usuario( datos: dict = Body(...),
    db: Session = Depends(get_db)
):
    usuario = crear_usuario(
        db=db,
        nombre=datos.get("nombre"),
        correo=datos.get("correo"),
        contrasena=datos.get("contrasena"),
        direccion=datos.get("direccion"),
        telefono=datos.get("telefono")
    )

    return {
        "id": usuario.id,
        "nombre": usuario.nombre,
        "correo": usuario.correo,
        "direccion": usuario.direccion,
        "telefono": usuario.telefono
    }
