import os
from fastapi import HTTPException
from app.repositorios.pago_repositorio import PagoRepositorio
from app.modelos.pago import Pago
#from transbank.common.webpay_options import WebpayOptions import que no es reconocido posiblemete por version de python 3.12
from transbank.webpay.webpay_plus.transaction import Transaction
from transbank.common.integration_type import IntegrationType


class PagoServicio:
    def __init__(self, repositorio: PagoRepositorio):
        self.repositorio = repositorio

        commerce_code = os.getenv("WEBPAY_COMMERCE_CODE", "597055555532")
        api_key = os.getenv("WEBPAY_API_KEY", "bfb279f2c...")  # usa tu API Key real
        environment = os.getenv("WEBPAY_ENVIRONMENT", "integration").lower()

        integration_type = (
            IntegrationType.TEST if environment == "integration" else IntegrationType.LIVE
        )

        # Configurar opciones de Webpay  (descomentar si es necesario) parte que tiene problemas con el import
        #options = WebpayOptions(
          #  commerce_code=commerce_code,
           # api_key=api_key,
           # integration_type=integration_type
       # )

        #self.webpay = Transaction(options)

    def iniciar_pago(self, monto: float, usuario_id: int, compra_id: int, moneda: str = "CLP") -> Pago:
        buy_order = f"ORD-{usuario_id}-{compra_id}"
        session_id = f"SESSION-{usuario_id}"
        return_url = os.getenv("WEBPAY_RETURN_URL", "https://miapp.cl/pagos/confirmar")

        try:
            respuesta = self.webpay.create(
                buy_order=buy_order,
                session_id=session_id,
                amount=monto,
                return_url=return_url
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error al iniciar transacción Webpay: {str(e)}")

        pago = self.repositorio.crear_pago(
            monto=monto,
            usuario_id=usuario_id,
            compra_id=compra_id,
            moneda=moneda,
            token=respuesta.token,
            url=respuesta.url
        )
        return pago

    def confirmar_pago(self, token_ws: str) -> Pago:
        pago = self.repositorio.obtener_por_token(token_ws)
        if not pago:
            raise HTTPException(status_code=404, detail="Pago no encontrado")

        try:
            resultado = self.webpay.commit(token_ws)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error al confirmar transacción Webpay: {str(e)}")

        if resultado.response_code == 0:
            return self.repositorio.marcar_como_aprobado(pago)
        else:
            return self.repositorio.marcar_como_rechazado(pago)

    def estado_pago(self, pago_id: int) -> Pago:
        pago = self.repositorio.obtener_por_id(pago_id)
        if not pago:
            raise HTTPException(status_code=404, detail="Pago no encontrado")
        return pago
