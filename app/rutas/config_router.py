# config_router.py

from fastapi import APIRouter, HTTPException
from app.servicios.config_service import obtener_ngrok_url, actualizar_config_js

# Crear el router
router = APIRouter(
    prefix="/config",
    tags=["configuracion"]
)

@router.get("/")
async def get_config():
    """
    Endpoint para obtener la configuración (NGROK_URL) para el frontend
    """
    try:
        # Intentar obtener la URL de ngrok
        ngrok_url = obtener_ngrok_url()
        
        if ngrok_url:
            return {"ngrok_url": ngrok_url}
        
        # Si no se pudo obtener, intentar regenerar config.js
        print("🔄 Regenerando config.js...")
        ngrok_url = actualizar_config_js()
        
        if ngrok_url:
            return {"ngrok_url": ngrok_url}
        
        raise HTTPException(
            status_code=500, 
            detail="No se pudo obtener NGROK_URL. Verifica el archivo .env"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error al obtener configuración: {str(e)}"
        )

@router.post("/refresh")
async def refresh_config():
    """
    Endpoint para forzar la actualización de la configuración
    """
    try:
        ngrok_url = actualizar_config_js()
        
        if ngrok_url:
            return {
                "message": "Configuración actualizada correctamente",
                "ngrok_url": ngrok_url
            }
        else:
            raise HTTPException(
                status_code=500,
                detail="No se pudo actualizar la configuración"
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al actualizar configuración: {str(e)}"
        )