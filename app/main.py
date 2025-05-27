import os
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security.api_key import APIKeyHeader
from starlette.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from app.base_de_datos import Base, motor
from app.rutas.productos import router as productos_router

# Carga variables de entorno
load_dotenv()

# --- Seguridad API Key ---
api_key_header = APIKeyHeader(name="X-API-KEY", auto_error=False)

def validar_api_key(api_key: str = Depends(api_key_header)) -> str:
    """
    Valida la API Key recibida en el header X-API-KEY.
    Devuelve 'interna' o 'externa' según corresponda.
    """
    if api_key == os.getenv("API_KEY_INTERNA"):
        return "interna"
    if api_key == os.getenv("API_KEY_EXTERNA"):
        return "externa"
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="API key inválida"
    )

# --- Configuración de la aplicación ---
app = FastAPI(title="Ferremas REST API")

# Crea tablas en desarrollo
Base.metadata.create_all(bind=motor)

# Middleware CORS (ajusta los orígenes a los dominios de tus clientes)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://tusucursal.com",
        "https://tienda-externa.com"
    ],
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["X-API-KEY", "Content-Type", "Authorization"],
)

# Incluye el router de productos,
# forzando la validación de API key en todas las rutas
app.include_router(
    productos_router,
    prefix="/productos",
    tags=["Productos"],
    dependencies=[Depends(validar_api_key)]
)
