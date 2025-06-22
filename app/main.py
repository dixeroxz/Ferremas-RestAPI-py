from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse, RedirectResponse
import os
from fastapi import Depends, FastAPI, HTTPException, Body
from starlette.middleware.cors import CORSMiddleware
from dotenv import load_dotenv, set_key
from pyngrok import ngrok, conf
from pathlib import Path

from app.base_de_datos import Base, motor
from app.dependencias import get_db
from app.rutas.usuario import router as usuario_router
from app.rutas.contacto import router as contacto_router
from app.rutas.productos import router as productos_router
from app.rutas.redireccion import router as redireccion_router
from app.rutas.compra import router as compra_router
from app.rutas.pagos import router as pagos_router
from app.rutas.divisas import router as divisas_router
from app.seguridad import validar_api_key_general
from app.rutas.config_router import router as config_router
from app.servicios.config_service import inicializar_configuracion, actualizar_config_js_con_url
from app.modelos.usuario import Usuario
from app.servicios.usuario_servicio import pwd_context

from sqlalchemy.orm import Session

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

# ngrok (solo si no es producción)
if os.getenv("ENV") != "PROD":
    tunnel = ngrok.connect(8000)
    public_url = tunnel.public_url
    print(f"\U0001F310 URL pública (ngrok): {public_url}")

    # Actualizar variables de entorno
    os.environ["NGROK_PUBLIC_URL"] = public_url
    os.environ["WEBPAY_RETURN_URL"] = f"{public_url}/pagos/confirmar"
    os.environ["FRONTEND_CONFIRM_URL"] = f"{public_url}/static/pago_exitoso.html"

    # Guardar en archivo .env
    set_key(env_path, "NGROK_PUBLIC_URL", public_url)
    set_key(env_path, "WEBPAY_RETURN_URL", f"{public_url}/pagos/confirmar")
    set_key(env_path, "FRONTEND_CONFIRM_URL", f"{public_url}/static/pago_exitoso.html")
    
    # 🔥 NUEVO: Actualizar config.js inmediatamente después de obtener la URL de ngrok
    print("🔄 Actualizando config.js con nueva URL de ngrok...")
    config_actualizado = actualizar_config_js_con_url(public_url)
    if config_actualizado:
        print("✅ config.js actualizado correctamente")
    else:
        print("❌ Error al actualizar config.js")

# Incluir routers protegidos
app.include_router(productos_router, prefix="/productos", tags=["Productos"], dependencies=[Depends(validar_api_key_general)])
app.include_router(compra_router, prefix="/compras", tags=["Compras"], dependencies=[Depends(validar_api_key_general)])
app.include_router(pagos_router, prefix="/pagos", tags=["Pagos"])
app.include_router(divisas_router, prefix="/divisas", tags=["Divisas"], dependencies=[Depends(validar_api_key_general)])
app.include_router(usuario_router, prefix="/usuarios", tags=["Usuarios"])
app.include_router(contacto_router, prefix="/contacto", tags=["Contacto"])
app.include_router(redireccion_router)
# 🔥 NUEVO: Incluir el router de configuración
app.include_router(config_router)

# Sirve carpeta static
app.mount("/static", StaticFiles(directory="static"), name="static")

# Evento de startup - se ejecuta después de que todo esté configurado
@app.on_event("startup")
async def startup_event():
    """
    Se ejecuta al iniciar el servidor - después de la configuración de ngrok
    """
    print("🚀 Servidor FastAPI iniciado completamente")
    
    # Verificar que la configuración esté correcta
    ngrok_url = os.getenv("NGROK_PUBLIC_URL")
    if ngrok_url:
        print(f"🔗 URL de ngrok configurada: {ngrok_url}")
        print(f"🌐 Frontend disponible en: {ngrok_url}/static/index.html")
    else:
        print("⚠️  No se detectó URL de ngrok - modo desarrollo local")

@app.get("/login")
def login():
    return FileResponse("static/login.html")

@app.get("/index")
def index():
    return FileResponse("static/index.html")

@app.get("/registro")
def registro():
    return FileResponse("static/registro.html")

@app.get("/perfil")
def perfil():
    return FileResponse("static/perfil.html")

@app.get("/gestion")
def gestion():
    return FileResponse("static/gestion.html")

@app.post("/login")
def login(
    datos: dict = Body(...),
    db: Session = Depends(get_db)
):
    correo = datos.get("correo")
    contrasena = datos.get("contrasena")

    if not correo or not contrasena:
        raise HTTPException(status_code=400, detail="Correo y contraseña son obligatorios")

    usuario = db.query(Usuario).filter(Usuario.correo == correo).first()

    if not usuario or not pwd_context.verify(contrasena, usuario.contrasena):
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")

    return {
        "id": usuario.id,
        "nombre": usuario.nombre,
        "correo": usuario.correo,
        "direccion": usuario.direccion,
        "telefono": usuario.telefono,
        "rol": usuario.rol if hasattr(usuario, "rol") else "cliente"
    }

# Ruta inicial
@app.get("")
def raiz():
    return RedirectResponse(url="/login")