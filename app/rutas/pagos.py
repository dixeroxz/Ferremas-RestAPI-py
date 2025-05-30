from fastapi import APIRouter, Depends, status, Form
from typing import Generator
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from app.base_de_datos import SesionLocal
from app.repositorios.pago_repositorio import PagoRepositorio
from app.servicios.pago_servicio import PagoServicio
from app.seguridad import validar_api_key_general

router = APIRouter(prefix="/pagos", tags=["Pagos"])

def obtener_sesion() -> Generator[Session, None, None]:
    db = SesionLocal()
    try:
        yield db
    finally:
        db.close()

def obtener_servicio(db: Session = Depends(obtener_sesion)) -> PagoServicio:
    return PagoServicio(PagoRepositorio(db))


# Esquemas

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

class ConfirmarPagoEntrada(BaseModel):
    token_ws: str = Field(..., example="TK_ORD-1001")


# Endpoints

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

@router.post(
    
    "/confirmar",
    response_model=PagoSalida,
    summary="Confirmar transacción de pago",
    dependencies=[Depends(validar_api_key_general)]
)
def confirmar_pago(
    token_ws: str = Form(...),
    servicio: PagoServicio = Depends(obtener_servicio)
):
    return servicio.confirmar_pago(token_ws)

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
