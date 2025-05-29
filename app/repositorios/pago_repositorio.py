from sqlalchemy.orm import Session
from app.modelos.pago import Pago, EstadoPago
from app.repositorios.compra_repositorio import CompraRepositorio
from datetime import datetime
import uuid

class PagoRepositorio:
    def __init__(self, db: Session):
        self.db = db

    def crear_pago(self, monto: float, usuario_id: int, compra_id: int, moneda: str = "CLP") -> Pago:
        order_id = str(uuid.uuid4())
        pago = Pago(
            order_id=order_id,
            monto=monto,
            moneda=moneda,
            usuario_id=usuario_id,
            compra_id=compra_id,
            estado=EstadoPago.PENDIENTE,
            fecha_creacion=datetime.utcnow(),
            fecha_actualizacion=datetime.utcnow()
        )
        self.db.add(pago)
        self.db.commit()
        self.db.refresh(pago)
        return pago

    def crear_transaccion_webpay(self, pago: Pago) -> Pago:
        """
        Simula la creación de una transacción en Webpay.
        Aquí debes integrar tu llamada real a la API o SDK de Webpay.
        """
        # Simulación respuesta Webpay
        token_generado = "token_" + str(uuid.uuid4())
        url_redireccion = f"https://webpay.cl/pago?token={token_generado}"

        pago.token = token_generado
        pago.url_redireccion = url_redireccion
        pago.fecha_actualizacion = datetime.utcnow()
        self.db.commit()
        self.db.refresh(pago)
        return pago

    def validar_pago_webpay(self, token: str) -> Pago:
        """
        Valida el estado del pago en Webpay y actualiza pago y compra.
        En producción, aquí consultas la API real de Webpay para confirmar estado.
        """
        pago = self.db.query(Pago).filter(Pago.token == token).first()
        if not pago:
            raise Exception("Pago no encontrado para token dado")

        # Simulación: chequea el estado de pago en Webpay
        # Resultado simulado (puede venir de API real)
        # Ejemplo estados: "APROBADO", "RECHAZADO", "PENDIENTE"
        estado_webpay = "APROBADO"  # Cambia según la lógica real

        compra_repo = CompraRepositorio(self.db)

        if estado_webpay == "APROBADO":
            pago.estado = EstadoPago.CONFIRMADO
            compra_repo.confirmar_compra(pago.compra_id)
        elif estado_webpay == "RECHAZADO":
            pago.estado = EstadoPago.RECHAZADO
            compra_repo.cancelar_compra(pago.compra_id)
        else:
            # Mantener pendiente o manejar otros estados
            pago.estado = EstadoPago.PENDIENTE

        pago.fecha_actualizacion = datetime.utcnow()
        self.db.commit()
        self.db.refresh(pago)
        return pago

    # Métodos para acceso y actualización manual si es necesario

    def actualizar_estado(self, pago: Pago, nuevo_estado: EstadoPago) -> Pago:
        pago.estado = nuevo_estado
        pago.fecha_actualizacion = datetime.utcnow()
        self.db.commit()
        self.db.refresh(pago)
        return pago

    def guardar_token_y_url(self, pago: Pago, token: str, url_redireccion: str) -> Pago:
        pago.token = token
        pago.url_redireccion = url_redireccion
        pago.fecha_actualizacion = datetime.utcnow()
        self.db.commit()
        self.db.refresh(pago)
        return pago

    def obtener_por_id(self, pago_id: int) -> Pago:
        return self.db.query(Pago).filter(Pago.id == pago_id).first()

    def obtener_por_order_id(self, order_id: str) -> Pago:
        return self.db.query(Pago).filter(Pago.order_id == order_id).first()

    def obtener_por_token(self, token: str) -> Pago:
        return self.db.query(Pago).filter(Pago.token == token).first()
