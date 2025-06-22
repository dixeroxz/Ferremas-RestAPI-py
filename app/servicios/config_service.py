# config_service.py

from dotenv import load_dotenv
import os
import re

def actualizar_config_js():
    """
    Actualiza el archivo config.js con datos del .env
    """
    try:
        # Cargar variables del archivo .env
        load_dotenv()
        
        NGROK_URL = os.getenv("NGROK_PUBLIC_URL")
        if NGROK_URL:
            NGROK_URL = NGROK_URL.strip("'\"")  # Elimina comillas si hay
        
        if not NGROK_URL:
            raise ValueError("Falta variable NGROK_PUBLIC_URL en .env")
        
        contenido_config_js = f"""const NGROK_URL = "{NGROK_URL}";"""
        
        with open("config.js", "w", encoding="utf-8") as f:
            f.write(contenido_config_js)
        
        print("✅ Archivo config.js generado correctamente con datos del .env")
        return NGROK_URL
    except Exception as e:
        print(f"❌ Error al generar config.js: {e}")
        return None

def obtener_ngrok_url():
    """
    Obtiene la URL de ngrok desde diferentes fuentes
    """
    try:
        # Opción 1: Leer desde config.js (si existe)
        if os.path.exists("config.js"):
            with open("config.js", "r", encoding="utf-8") as f:
                content = f.read()
                match = re.search(r'NGROK_URL\s*=\s*["\']([^"\']+)["\']', content)
                if match:
                    return match.group(1)
        
        # Opción 2: Si no existe config.js, leer directamente del .env
        load_dotenv()
        NGROK_URL = os.getenv("NGROK_PUBLIC_URL")
        if NGROK_URL:
            return NGROK_URL.strip("'\"")
        
        return None
        
    except Exception as e:
        print(f"❌ Error al obtener NGROK_URL: {e}")
        return None

def actualizar_config_js_con_url(ngrok_url):
    """
    Actualiza config.js con una URL específica de ngrok
    """
    try:
        if not ngrok_url:
            raise ValueError("URL de ngrok es requerida")
        
        # Limpiar la URL (quitar barra final si existe)
        ngrok_url = ngrok_url.rstrip('/')
        
        contenido_config_js = f"""const NGROK_URL = "{ngrok_url}";"""
        
        with open("config.js", "w", encoding="utf-8") as f:
            f.write(contenido_config_js)
        
        print("✅ Archivo config.js actualizado con URL específica")
        return True
    except Exception as e:
        print(f"❌ Error al actualizar config.js con URL específica: {e}")
        return False

def inicializar_configuracion():
    """
    Función para inicializar la configuración al arranque
    """
    print("🔧 Inicializando configuración...")
    
    # Actualizar config.js con la URL actual de ngrok
    ngrok_url = actualizar_config_js()
    if ngrok_url:
        print(f"🔗 NGROK_URL configurada: {ngrok_url}")
        return True
    else:
        print("⚠️  Advertencia: No se pudo configurar NGROK_URL")
        return False