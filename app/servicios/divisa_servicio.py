import os
import httpx
from fastapi import HTTPException
from datetime import date

class DivisaServicio:
    BASE_URL = "https://api.sbif.cl/api-sbifv3/recursos_api"

    def __init__(self):
        token = os.getenv("APIKEY_BCCH")
        if not token:
            raise RuntimeError("Falta APIKEY_BCCH en el entorno (.env)")
        self.token = token

    async def obtener_tasa(self, fecha: date | None = None) -> float:
        """
        - Sin fecha → /dolar
        - Con fecha → /dolar/YYYY/MM/dias/DD
        """
        if fecha:
            url = f"{self.BASE_URL}/dolar/{fecha.year}/{fecha.month:02d}/dias/{fecha.day:02d}"
        else:
            url = f"{self.BASE_URL}/dolar"

        params = {"apikey": self.token, "formato": "json"}

        try:
            async with httpx.AsyncClient(follow_redirects=True) as client:
                resp = await client.get(url, params=params, timeout=10.0)
        except httpx.RequestError as e:
            raise HTTPException(502, f"Error de conexión a SBIF: {e}")

        if resp.status_code != 200:
            raise HTTPException(502, f"SBIF respondió {resp.status_code}")

        try:
            body = resp.json()
        except ValueError:
            raise HTTPException(502, "SBIF no devolvió JSON válido")

        # {"Dolares":[{"Fecha":"YYYY-MM-DD","Valor":"828,50"}]}
        try:
            entrada = body["Dolares"][0]
            valor = float(entrada["Valor"].replace(".", "").replace(",", "."))
            return valor
        except (KeyError, IndexError, ValueError) as e:
            detail = {"body": body, "error": str(e)}
            raise HTTPException(500, f"Formato SBIF inesperado: {detail}")

    async def convertir(self, monto: float, origen: str, destino: str) -> float:
        origen = origen.upper()
        destino = destino.upper()
        if origen == destino:
            return monto

        tasa = await self.obtener_tasa(None)
        if origen == "USD" and destino == "CLP":
            return monto * tasa
        if origen == "CLP" and destino == "USD":
            return monto / tasa

        raise HTTPException(400, "Par de divisas no soportado (solo USD↔CLP)")
