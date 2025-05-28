from fastapi import HTTPException
from app.repositorios.pago_repositorio import PagoRepositorio
from app.modelos.pago import EstadoPago, Pago
from typing import Tuple

class PagoServicio:
    def __init__(self, repositorio: PagoRepositorio):
        self.repositorio = repositorio
        # Aquí carga credenciales de Webpay desde .env o configuración
        # e.g. self.webpay_client = WebpayClient(api_key=...)

    def iniciar_pago(self, order_id: str, monto: float, moneda: str = "CLP") -> Pago:
        # 1) Lógica para llamar a Webpay y obtener token + URL redirección
        # Ejemplo ficticio:
        token = f"TK_{order_id}"
        url = f"https://webpay.example.com/pay/{token}"
        # 2) Guardar en BD
        pago = self.repositorio.crear_pago(order_id, monto, moneda, token, url)
        return pago

    def confirmar_pago(self, order_id: str, token_ws: str) -> Pago:
        pago = self.repositorio.obtener_por_order_id(order_id)
        if not pago:
            raise HTTPException(status_code=404, detail="Pago no encontrado")
        # 1) Llamada a Webpay para confirmar: response = webpay_client.confirm(token_ws)
        # Simular confirmación exitosa:
        exitoso = True
        if exitoso:
            pago = self.repositorio.actualizar_estado(pago, EstadoPago.APROBADO)
        else:
            pago = self.repositorio.actualizar_estado(pago, EstadoPago.RECHAZADO)
        return pago

    def cancelar_pago(self, order_id: str) -> Pago:
        pago = self.repositorio.obtener_por_order_id(order_id)
        if not pago:
            raise HTTPException(status_code=404, detail="Pago no encontrado")
        # Llamada a Webpay para anular
        pago = self.repositorio.actualizar_estado(pago, EstadoPago.ANULADO)
        return pago

    def estado_pago(self, pago_id: int) -> Pago:
        pago = self.repositorio.obtener_por_id(pago_id)
        if not pago:
            raise HTTPException(status_code=404, detail="Pago no encontrado")
        return pago
