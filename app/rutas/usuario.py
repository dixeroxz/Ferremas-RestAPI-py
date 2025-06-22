from app.modelos.usuario import Usuario
from app.seguridad import validar_api_key_general
from fastapi import APIRouter, Depends, Body
from sqlalchemy.orm import Session
from app.dependencias import get_db
from app.servicios.usuario_servicio import crear_usuario
from fastapi import HTTPException

router = APIRouter()

@router.post("")
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
        "telefono": usuario.telefono,
        "rol": usuario.rol if hasattr(usuario, "rol") else "cliente"
    }

@router.get("/{id}", dependencies=[Depends(validar_api_key_general)])
def obtener_usuario(id: int, db: Session = Depends(get_db)):
    usuario = db.query(Usuario).filter(Usuario.id == id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    return {
        "id": usuario.id,
        "nombre": usuario.nombre,
        "correo": usuario.correo,
        "direccion": usuario.direccion,
        "telefono": usuario.telefono,
        "rol": usuario.rol if hasattr(usuario, "rol") else "cliente"
    }


@router.put("/{id}", dependencies=[Depends(validar_api_key_general)])
def actualizar_usuario(id: int, datos: dict = Body(...), db: Session = Depends(get_db)):
    usuario = db.query(Usuario).filter(Usuario.id == id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    # Validación: Solo puede editarse a sí mismo
    if datos.get("id") and datos["id"] != id:
        raise HTTPException(status_code=403, detail="No puedes modificar otro perfil")

    usuario.nombre = datos.get("nombre", usuario.nombre)
    usuario.direccion = datos.get("direccion", usuario.direccion)
    usuario.telefono = datos.get("telefono", usuario.telefono)

    db.commit()
    db.refresh(usuario)

    return {
        "id": usuario.id,
        "nombre": usuario.nombre,
        "correo": usuario.correo,
        "direccion": usuario.direccion,
        "telefono": usuario.telefono,
        "rol": usuario.rol if hasattr(usuario, "rol") else "cliente"
    }
