from sqlalchemy.orm import Session
from app.modelos.usuario import Usuario
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError

def crear_usuario(db: Session, nombre: str, correo: str, contrasena: str, direccion: str = None, telefono: str = None):
    existente = db.query(Usuario).filter(Usuario.correo == correo).first()
    if existente:
        raise HTTPException(status_code=400, detail="El correo ya está registrado")

    nuevo_usuario = Usuario(
        nombre=nombre,
        correo=correo,
        contrasena=contrasena,
        direccion=direccion,
        telefono=telefono
    )

    try:
        db.add(nuevo_usuario)
        db.commit()
        db.refresh(nuevo_usuario)
        return nuevo_usuario
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Error al guardar el usuario")
