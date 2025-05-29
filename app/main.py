import os
from fastapi import Depends, FastAPI
from starlette.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

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
