import os
from fastapi import Depends, FastAPI
from starlette.middleware.cors import CORSMiddleware
from dotenv import load_dotenv, set_key
from pyngrok import ngrok, conf
from pathlib import Path

from app.base_de_datos import Base, motor
from app.rutas.usuario import router as usuario_router
from app.rutas.contacto import router as contacto_router
from app.rutas.productos import router as productos_router
from app.rutas.redireccion import router as redireccion_router
from app.rutas.compra import router as compra_router
from app.rutas.pagos import router as pagos_router
from app.rutas.divisas import router as divisas_router
from app.seguridad import validar_api_key_general

# Ruta absoluta al archivo .env
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

# Configura pyngrok con el token de autenticación
conf.get_default().auth_token = os.getenv("NGROK_AUTHTOKEN")

# Crear la aplicación FastAPI
app = FastAPI(title="Ferremas REST API")

# Crear las tablas en la base de datos
Base.metadata.create_all(bind=motor)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["X-API-KEY", "Content-Type", "Authorization"],
)

# Solo usar ngrok si no estás en entorno de producción
if os.getenv("ENV") != "PROD":
    tunnel = ngrok.connect(8000)
    public_url = tunnel.public_url  # URL limpia (ej. https://abcd.ngrok-free.app)
    print(f"\U0001F310 URL pública (ngrok): {public_url}")

    # Actualizar variables de entorno en ejecución
    os.environ["NGROK_PUBLIC_URL"] = public_url
    os.environ["WEBPAY_RETURN_URL"] = f"{public_url}/pagos/confirmar"

    # Actualizar también en el archivo .env
    set_key(env_path, "NGROK_PUBLIC_URL", public_url)
    set_key(env_path, "WEBPAY_RETURN_URL", f"{public_url}/pagos/confirmar")

# Incluir routers
app.include_router(
    productos_router,
    prefix="/productos",
    tags=["Productos"],
    dependencies=[Depends(validar_api_key_general)]
)

app.include_router(
    compra_router,
    prefix="/compras",
    tags=["Compras"],
    dependencies=[Depends(validar_api_key_general)]
)

app.include_router(
    pagos_router,
    prefix="/pagos",
    tags=["Pagos"],   
)

app.include_router(
    divisas_router,
    prefix="/divisas",
    tags=["Divisas"],
    dependencies=[Depends(validar_api_key_general)]
)

app.include_router(
    usuario_router,
    prefix="/usuarios",
    tags=["Usuarios"],
    dependencies=[Depends(validar_api_key_general)]
)

app.include_router(
    contacto_router,
    prefix="/contacto",
    tags=["Contacto"]
)

app.include_router(redireccion_router)
