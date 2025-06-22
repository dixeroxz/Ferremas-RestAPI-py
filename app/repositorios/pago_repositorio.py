from sqlalchemy.orm import Session
from app.modelos.pago import Pago
from app.repositorios.compra_repositorio import CompraRepositorio
from datetime import datetime

class PagoRepositorio:
    def __init__(self, db: Session):
        self.db = db

    def crear_pago(self, monto: float, usuario_id: int, compra_id: int, moneda: str, token: str, url: str) -> Pago:
        pago = Pago(
            monto=monto,
            moneda=moneda,
            usuario_id=usuario_id,
            compra_id=compra_id,
            token=token,
            url_redireccion=url,
            fecha_creacion=datetime.utcnow(),
            fecha_actualizacion=datetime.utcnow()
        )
        self.db.add(pago)
        self.db.commit()
        self.db.refresh(pago)
        return pago

    def marcar_como_aprobado(self, pago: Pago) -> Pago:
        try:
            # Cambiar estado de la compra asociada a "APROBADO"
            compra_repo = CompraRepositorio(self.db)
            compra_repo.confirmar_compra(pago.compra_id)

            # Actualizar fecha de actualización del pago
            pago.fecha_actualizacion = datetime.utcnow()
            self.db.commit()
            self.db.refresh(pago)
            return pago
        except Exception as e:
            self.db.rollback()
            raise e

    def marcar_como_rechazado(self, pago: Pago) -> Pago:
        try:
            # Cambiar estado de la compra asociada a "RECHAZADO"
            compra_repo = CompraRepositorio(self.db)
            compra_repo.cancelar_compra(pago.compra_id)

            # Actualizar fecha de actualización del pago
            pago.fecha_actualizacion = datetime.utcnow()
            self.db.commit()
            self.db.refresh(pago)
            return pago
        except Exception as e:
            self.db.rollback()
            raise e

    def obtener_por_id(self, pago_id: int) -> Pago:
        return self.db.query(Pago).filter(Pago.id == pago_id).first()

    def obtener_por_token(self, token: str) -> Pago:
        return self.db.query(Pago).filter(Pago.token == token).first()
    
    def obtener_todos_los_pagos(self):
        return self.db.query(Pago).all()
    
    def obtener_pagos_por_usuario(self, usuario_id: int):
        return self.db.query(Pago).filter(Pago.usuario_id == usuario_id).all()