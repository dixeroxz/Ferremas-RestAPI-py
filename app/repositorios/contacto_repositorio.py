from sqlalchemy.orm import Session
from app.modelos.contacto import Contacto

class ContactoRepositorio:
    def __init__(self, db: Session):
        self.db = db

    def crear(self, nombre: str, email: str, asunto: str, mensaje: str) -> Contacto:
        nuevo = Contacto(
            nombre=nombre,
            email=email,
            asunto=asunto,
            mensaje=mensaje
        )
        self.db.add(nuevo)
        self.db.commit()
        self.db.refresh(nuevo)
        return nuevo

    def listar_todos(self) -> list[Contacto]:
        return (
            self.db
            .query(Contacto)
            .order_by(Contacto.fecha.desc())
            .all()
        )
