import os
from fastapi import Depends, FastAPI
from starlette.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from app.base_de_datos import Base, motor

from app.rutas.contacto import router as contacto_router
from app.rutas.productos import router as productos_router
from app.rutas.pagos import router as pagos_router
from app.rutas.divisas import router as divisas_router
from app.seguridad import validar_api_key_general

load_dotenv()

app = FastAPI(title="Ferremas REST API")

# Crear tablas en desarrollo
Base.metadata.create_all(bind=motor)

# CORS (ajusta orígenes si quieres limitar)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["X-API-KEY", "Content-Type", "Authorization"],
)

# Inyecta la validación general en todas las rutas de productos
app.include_router(
    productos_router,
    prefix="/productos",
    tags=["Productos"],
    dependencies=[Depends(validar_api_key_general)]
)

# Contacto
app.include_router(
    contacto_router
)

# Pagos
app.include_router(contacto_router)
app.include_router(pagos_router)
app.include_router(divisas_router)
