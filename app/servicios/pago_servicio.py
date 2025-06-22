import os
from fastapi import HTTPException
from fastapi.responses import RedirectResponse
from app.repositorios.pago_repositorio import PagoRepositorio
from app.repositorios.compra_repositorio import CompraRepositorio
from app.modelos.pago import Pago
from transbank.webpay.webpay_plus.transaction import Transaction


class PagoServicio:
    def __init__(self, repositorio: PagoRepositorio):
        self.repositorio = repositorio
        
        commerce_code = os.getenv("WEBPAY_COMMERCE_CODE")
        api_key = os.getenv("WEBPAY_API_KEY")
        
        # Construir instancia sin integration_type
        self.webpay = Transaction.build_for_integration(
            commerce_code=commerce_code,
            api_key=api_key
        )

    def iniciar_pago(self, monto: float, usuario_id: int, compra_id: int, moneda: str = "CLP") -> Pago:
        buy_order = f"ORD-{usuario_id}-{compra_id}"
        session_id = f"SESSION-{usuario_id}"
        # IMPORTANTE: Esta debe ser la URL de tu endpoint backend
        return_url = os.getenv("WEBPAY_RETURN_URL")  # Ej: https://tu-backend.ngrok.io/pagos/confirmar
        
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
            token=respuesta["token"],
            url=respuesta["url"]
        )
        return pago

    def confirmar_pago(self, token_ws: str) -> Pago:
        """
        Este método procesa el pago y retorna el objeto Pago.
        Debe ser llamado desde el endpoint que maneja el return_url.
        """
        pago = self.repositorio.obtener_por_token(token_ws)
        if not pago:
            raise HTTPException(status_code=404, detail="Pago no encontrado")
        
        try:
            resultado = self.webpay.commit(token_ws)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error al confirmar transacción Webpay: {str(e)}")
        
        # Procesar resultado - los métodos del repositorio ya manejan la compra
        if resultado["response_code"] == 0:
            return self.repositorio.marcar_como_aprobado(pago)
        else:
            return self.repositorio.marcar_como_rechazado(pago)

    def procesar_y_redirigir(self, token_ws: str) -> RedirectResponse:
        """
        Este método procesa el pago y redirige al frontend con el resultado.
        Úsalo en tu endpoint de confirmación.
        """
        try:
            pago = self.confirmar_pago(token_ws)
            frontend_url = os.getenv("FRONTEND_CONFIRM_URL")
            print("Redirigiendo a:", frontend_url)
            
            # Obtener información de la compra para verificar el estado
            compra_repo = CompraRepositorio(self.repositorio.db)
            compra = compra_repo.obtener_por_id(pago.compra_id)
            
            # Verificar el estado basado en la compra
            if compra and compra.estado == "APROBADO":  # Ajusta según tu enum/string de estados
                return RedirectResponse(
                    url=f"{frontend_url}?status=success&pago_id={pago.id}&compra_id={pago.compra_id}&monto={pago.monto}&estado_compra={compra.estado}",
                    status_code=302
                )
            else:
                estado_compra = compra.estado if compra else "DESCONOCIDO"
                return RedirectResponse(
                    url=f"{frontend_url}?status=error&pago_id={pago.id}&compra_id={pago.compra_id}&mensaje=Pago rechazado&estado_compra={estado_compra}",
                    status_code=302
                )
                
        except HTTPException as e:
            frontend_url = os.getenv("FRONTEND_CONFIRM_URL")
            return RedirectResponse(
                url=f"{frontend_url}?status=error&mensaje={e.detail}",
                status_code=302
            )
        except Exception as e:
            frontend_url = os.getenv("FRONTEND_CONFIRM_URL")
            return RedirectResponse(
                url=f"{frontend_url}?status=error&mensaje=Error interno del servidor",
                status_code=302
            )

    def estado_pago(self, pago_id: int) -> Pago:
        pago = self.repositorio.obtener_por_id(pago_id)
        if not pago:
            raise HTTPException(status_code=404, detail="Pago no encontrado")
        return pago