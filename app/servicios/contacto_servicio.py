from fastapi import HTTPException
from app.repositorios.contacto_repositorio import ContactoRepositorio
from app.modelos.contacto import Contacto

class ContactoServicio:
    def __init__(self, repositorio: ContactoRepositorio):
        self.repositorio = repositorio

    def enviar_mensaje(self, nombre: str, email: str, asunto: str, mensaje: str) -> Contacto:
        # Podrías añadir validaciones (email válido, spam, etc.)
        return self.repositorio.crear(nombre, email, asunto, mensaje)

    def listar_mensajes(self) -> list[Contacto]:
        mensajes = self.repositorio.listar_todos()
        if not mensajes:
            raise HTTPException(status_code=404, detail="No hay mensajes registrados")
        return mensajes
