from fastapi import APIRouter, Depends, Query
from typing import Optional
from datetime import date
from pydantic import BaseModel, Field

from app.servicios.divisa_servicio import DivisaServicio

router = APIRouter(prefix="/divisas", tags=["Divisas"])

def get_divisa_servicio() -> DivisaServicio:
    return DivisaServicio()

class TasaSalida(BaseModel):
    fecha: date
    tasa_usd_clp: float = Field(..., description="Valor de 1 USD en CLP según SBIF")

class ConvertirSalida(BaseModel):
    monto_original: float
    origen: str
    destino: str
    monto_convertido: float

@router.get(
    "/tasa",
    response_model=TasaSalida,
    summary="Tasa USD→CLP (SBIF, última o histórica)"
)
async def obtener_tasa(
    fecha: Optional[date] = Query(None, description="YYYY-MM-DD"),
    servicio: DivisaServicio = Depends(get_divisa_servicio)
):
    tasa = await servicio.obtener_tasa(fecha)
    return {"fecha": fecha or date.today(), "tasa_usd_clp": tasa}

@router.get(
    "/convertir",
    response_model=ConvertirSalida,
    summary="Convertir entre USD y CLP usando SBIF"
)
async def convertir(
    monto: float = Query(..., gt=0, description="Cantidad a convertir"),
    origen: str = Query("USD", description="USD o CLP"),
    destino: str = Query("CLP", description="USD o CLP"),
    servicio: DivisaServicio = Depends(get_divisa_servicio)
):
    resultado = await servicio.convertir(monto, origen, destino)
    return {
        "monto_original": monto,
        "origen": origen.upper(),
        "destino": destino.upper(),
        "monto_convertido": resultado
    }
