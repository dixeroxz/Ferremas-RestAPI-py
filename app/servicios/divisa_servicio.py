import httpx
from fastapi import HTTPException
from datetime import datetime

class DivisaServicio:
    BASE_URL = "https://api.sbif.cl/api-sbifv3/recursos_api"  # ejemplo

    def __init__(self, token: str):
        self.token = token

    async def obtener_tasa(self, fecha: datetime | None = None) -> float:
        """
        Llama a la API del BCCh y retorna la UF (o dólar) del día dado.
        Si fecha es None, usa la última.
        """
        params = {
            "apikey": self.token,
            "formato": "json",
        }
        if fecha:
            params["fecha"] = fecha.strftime("%Y-%m-%d")
        url = f"{self.BASE_URL}/dolar"
        async with httpx.AsyncClient() as client:
            resp = await client.get(url, params=params)
        if resp.status_code != 200:
            raise HTTPException(502, "Error al obtener tasa del BCCh")
        data = resp.json()
        # Extrae valor según estructura de la API SBIF
        try:
            valor = float(data["Dolares"][0]["Valor"])
            return valor
        except Exception:
            raise HTTPException(500, "Formato de tasa inesperado")

    async def convertir(self, monto: float, origen: str, destino: str) -> float:
        """
        Convierte monto de origen→CLP o CLP→origen usando obtener_tasa.
        Solo soporta CLP y USD por ahora.
        """
        origen = origen.upper()
        destino = destino.upper()
        if origen == destino:
            return monto
        tasa = await self.obtener_tasa()
        if origen == "USD" and destino == "CLP":
            return monto * tasa
        if origen == "CLP" and destino == "USD":
            return monto / tasa
        raise HTTPException(400, "Par de divisas no soportado")
