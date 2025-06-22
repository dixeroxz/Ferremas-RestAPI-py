import os
from fastapi import APIRouter, Depends, status, Form, Request
from typing import Generator
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from app.base_de_datos import SesionLocal
from app.repositorios.pago_repositorio import PagoRepositorio
from app.servicios.pago_servicio import PagoServicio
from app.seguridad import validar_api_key_general

router = APIRouter(tags=["Pagos"])

def obtener_sesion() -> Generator[Session, None, None]:
    db = SesionLocal()
    try:
        yield db
    finally:
        db.close()

def obtener_servicio(db: Session = Depends(obtener_sesion)) -> PagoServicio:
    return PagoServicio(PagoRepositorio(db))

class IniciarPagoEntrada(BaseModel):
    monto: float = Field(..., gt=0, example=150000.00)
    moneda: str = Field("CLP", example="USD")
    usuario_id: int = Field(..., example=12)
    compra_id: int = Field(..., example=34)

class PagoSalida(BaseModel):
    id: int
    monto: float
    moneda: str
    token: str | None
    url_redireccion: str | None

    class Config:
        from_attributes = True

@router.post(
    "/iniciar",
    response_model=PagoSalida,
    status_code=status.HTTP_201_CREATED,
    summary="Iniciar transacción de pago",
    dependencies=[Depends(validar_api_key_general)]
)
def iniciar_pago(
    entrada: IniciarPagoEntrada,
    servicio: PagoServicio = Depends(obtener_servicio)
):
    return servicio.iniciar_pago(entrada.monto, entrada.usuario_id, entrada.compra_id, entrada.moneda)

@router.api_route(
    "/confirmar",
    methods=["GET", "POST"],
    summary="Confirmar transacción y redirigir",
)
def confirmar_y_redirigir(
    request: Request,
    token_ws: str = Form(None),
    servicio: PagoServicio = Depends(obtener_servicio)
):
    if request.method == "GET":
        token_ws = request.query_params.get("token_ws")
        if not token_ws:
            return RedirectResponse(
                url=f"{os.getenv('FRONTEND_CONFIRM_URL')}?status=error&mensaje=Falta+el+token_ws+en+la+URL",
                status_code=302
            )
    elif not token_ws:
        return RedirectResponse(
            url=f"{os.getenv('FRONTEND_CONFIRM_URL')}?status=error&mensaje=Falta+el+token_ws+en+el+formulario",
            status_code=302
        )

    return servicio.procesar_y_redirigir(token_ws)

@router.get(
    "/estado/{pago_id}",
    response_model=PagoSalida,
    summary="Obtener estado de un pago",
    dependencies=[Depends(validar_api_key_general)]
)
def estado_pago(
    pago_id: int,
    servicio: PagoServicio = Depends(obtener_servicio)
):
    return servicio.estado_pago(pago_id)
