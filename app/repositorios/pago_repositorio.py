from sqlalchemy.orm import Session
from app.modelos.pago import Pago, EstadoPago
from datetime import datetime

class PagoRepositorio:
    def __init__(self, db: Session):
        self.db = db

    def crear_pago(self, order_id: str, monto: float, moneda: str = "CLP", token: str = None, url_redireccion: str = None) -> Pago:
        pago = Pago(
            order_id=order_id,
            monto=monto,
            moneda=moneda,
            token=token,
            url_redireccion=url_redireccion
        )
        self.db.add(pago)
        self.db.commit()
        self.db.refresh(pago)
        return pago

    def actualizar_estado(self, pago: Pago, nuevo_estado: EstadoPago) -> Pago:
        pago.estado = nuevo_estado
        pago.fecha_actualizacion = datetime.utcnow()
        self.db.add(pago)
        self.db.commit()
        self.db.refresh(pago)
        return pago

    def obtener_por_id(self, pago_id: int) -> Pago | None:
        return self.db.query(Pago).filter(Pago.id == pago_id).first()

    def obtener_por_order_id(self, order_id: str) -> Pago | None:
        return self.db.query(Pago).filter(Pago.order_id == order_id).first()
