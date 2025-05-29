from sqlalchemy.orm import Session
from app.modelos.usuario import Usuario
from passlib.context import CryptContext
from fastapi import HTTPException

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verificar_correo(correo: str) -> bool:
    return "@" in correo and "." in correo

def crear_usuario(db: Session, nombre: str, correo: str, contrasena: str, direccion: str = None, telefono: str = None):
    if not nombre or not correo or not contrasena:
        raise HTTPException(status_code=400, detail="Nombre, correo y contraseña son obligatorios")

    if not verificar_correo(correo):
        raise HTTPException(status_code=400, detail="Correo no válido")

    usuario_existente = db.query(Usuario).filter(Usuario.correo == correo).first()
    if usuario_existente:
        raise HTTPException(status_code=400, detail="El correo ya está registrado")

    contrasena_hash = pwd_context.hash(contrasena)

    nuevo_usuario = Usuario(
        nombre=nombre,
        correo=correo,
        contrasena=contrasena_hash,
        direccion=direccion,
        telefono=telefono
    )

    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)
    return nuevo_usuario
