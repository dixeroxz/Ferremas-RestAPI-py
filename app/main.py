import os
from fastapi import Depends, FastAPI
from starlette.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# 🔌 NGROK
from pyngrok import ngrok

from app.base_de_datos import Base, motor
from app.rutas.usuario import router as usuario_router
from app.rutas.contacto import router as contacto_router
from app.rutas.productos import router as productos_router
from app.rutas.compra import router as compra_router
from app.modelos.usuario import Usuario
from app.modelos.compra import Compra
from app.modelos.detalle_compras import DetalleCompras
from app.modelos.pago import Pago
from app.rutas.pagos import router as pagos_router
from app.rutas.divisas import router as divisas_router
from app.seguridad import validar_api_key_general

# Cargar variables de entorno
load_dotenv()

from pyngrok import conf
conf.get_default().auth_token = os.getenv("NGROK_AUTHTOKEN")

# Crear instancia de la app
app = FastAPI(title="Ferremas REST API")

# Crear tablas en la base de datos
Base.metadata.create_all(bind=motor)

# Configurar CORS (ajusta orígenes según sea necesario)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, restringe los orígenes
    allow_methods=["*"],
    allow_headers=["X-API-KEY", "Content-Type", "Authorization"],
)


if os.getenv("ENV") != "PROD":
    public_url = ngrok.connect(8000)
    print(f"🌐 URL pública (ngrok): {public_url}")
    os.environ["NGROK_PUBLIC_URL"] = str(public_url)

# Rutas protegidas con validación de API Key
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
    dependencies=[Depends(validar_api_key_general)]
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

# Ruta pública de contacto
app.include_router(
    contacto_router,
    prefix="/contacto",
    tags=["Contacto"]
)
