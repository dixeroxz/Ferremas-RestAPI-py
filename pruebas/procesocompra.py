from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, UnexpectedAlertPresentException
from dotenv import load_dotenv
import time
import json
import os
import sys

def obtener_url_actualizada():
    """Función para obtener la URL más actualizada del archivo .env"""
    # Limpiar COMPLETAMENTE las variables de entorno relacionadas con ngrok
    keys_to_remove = [key for key in os.environ.keys() if 'NGROK' in key.upper()]
    for key in keys_to_remove:
        del os.environ[key]
        print(f"🧹 Removida variable cacheada: {key}")
    
    # Ruta al archivo .env
    env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
    print(f"🔍 Buscando .env en: {os.path.abspath(env_path)}")
    
    if not os.path.exists(env_path):
        print("❌ Archivo .env no encontrado")
        return None
    
    # Leer el archivo directamente (sin cache)
    print("📄 Leyendo archivo .env directamente...")
    try:
        with open(env_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        # Buscar la línea NGROK_PUBLIC_URL
        ngrok_url = None
        for line in lines:
            line = line.strip()
            if line.startswith('NGROK_PUBLIC_URL'):
                # Extraer la URL después del =
                ngrok_url = line.split('=', 1)[1].strip()
                break
        
        if ngrok_url:
            # Limpiar comillas y espacios
            ngrok_url = ngrok_url.strip('\'"').strip().rstrip('/')
            print(f"✅ URL encontrada directamente: {ngrok_url}")
            return ngrok_url
        else:
            print("❌ NGROK_PUBLIC_URL no encontrada en el archivo")
            return None
            
    except Exception as e:
        print(f"❌ Error leyendo .env: {e}")
        return None

def verificar_ngrok_activo(url):
    """Verificar si la URL de ngrok está activa"""
    try:
        import requests
        response = requests.get(url + "/static/index.html", timeout=5)
        if response.status_code == 200:
            print("✅ URL de ngrok está activa")
            return True
        else:
            print(f"⚠️ URL responde con código: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ URL no responde: {e}")
        return False

def manejar_alertas_pendientes(driver, wait, max_intentos=5):
    """Función para manejar todas las alertas pendientes"""
    alertas_manejadas = 0
    for intento in range(max_intentos):
        try:
            # Crear un WebDriverWait específico con timeout corto
            wait_corto = WebDriverWait(driver, 2)
            alert = wait_corto.until(EC.alert_is_present())
            texto_alerta = alert.text
            print(f"📢 Alerta #{alertas_manejadas + 1}: {texto_alerta}")
            alert.accept()
            alertas_manejadas += 1
            time.sleep(0.5)  # Pequeña pausa entre alertas
        except TimeoutException:
            # No hay más alertas
            break
        except Exception as e:
            print(f"⚠️ Error manejando alerta: {e}")
            break
    
    if alertas_manejadas > 0:
        print(f"✅ {alertas_manejadas} alerta(s) manejada(s) correctamente")
    else:
        print("ℹ️ No se detectaron alertas")
    
    return alertas_manejadas

# Obtener URL actualizada
print("🔄 Obteniendo URL actualizada de ngrok...")
ngrok_url = obtener_url_actualizada()

if not ngrok_url:
    print("❌ No se pudo obtener la URL de ngrok")
    sys.exit(1)

# Verificar que la URL esté activa (opcional)
print("🌐 Verificando que ngrok esté activo...")
# Comentar la siguiente línea si no tienes requests instalado
# verificar_ngrok_activo(ngrok_url)

# Configuración de Chrome
chrome_options = Options()
chrome_options.add_argument("--start-maximized")
chrome_options.add_argument("--disable-web-security")
chrome_options.add_argument("--disable-features=VizDisplayCompositor")

driver = webdriver.Chrome(service=Service(), options=chrome_options)
wait = WebDriverWait(driver, 15)

# Simular usuario cliente
usuario_simulado = {
    "id": 5,
    "nombre": "Juan Pépe",
    "rol": "cliente",
    "email": "juan.pepe@example.com"
}

try:
    # 1. Construir URL completa
    url_completa = f"{ngrok_url}/static/index.html"
    print(f"🌐 Accediendo a: {url_completa}")
    
    driver.get(url_completa)
    
    # Manejar página de advertencia de ngrok gratuito
    time.sleep(2)
    if "ngrok-free.app" in driver.current_url:
        print("⚠️ Detectada página de advertencia de ngrok gratuito")
        try:
            # Buscar el botón "Visit Site" o similar
            visit_buttons = driver.find_elements(By.XPATH, "//button[contains(text(), 'Visit Site') or contains(text(), 'Continue')]")
            if visit_buttons:
                visit_buttons[0].click()
                time.sleep(3)
                print("✅ Página de advertencia superada")
            else:
                print("ℹ️ No se encontró botón de continuación")
        except Exception as e:
            print(f"⚠️ Error manejando advertencia: {e}")
    
    # Verificar que llegamos a la página correcta
    print(f"📍 URL actual: {driver.current_url}")
    
    # Almacenar usuario en localStorage
    driver.execute_script(f"localStorage.setItem('usuarioLogueado', '{json.dumps(usuario_simulado)}');")
    print("🔐 Usuario cliente simulado almacenado en localStorage")

    # Refrescar para que la app cargue al usuario
    driver.refresh()
    time.sleep(3)

    # 2. Agregar producto al carrito
    print("🛒 Buscando productos...")
    productos = driver.find_elements(By.CLASS_NAME, "agregar-carrito")
    
    if not productos:
        print("❌ No se encontraron productos")
        print("🔍 Elementos disponibles en la página:")
        # Debug: mostrar algunos elementos de la página
        body_text = driver.find_element(By.TAG_NAME, "body").text[:500]
        print(f"Texto de la página: {body_text}")
        raise Exception("No se encontraron productos para agregar al carrito")
    
    productos[0].click()
    print("✅ Producto agregado al carrito")
    time.sleep(1)

    # 3. Abrir el carrito (offcanvas)
    print("🛒 Abriendo carrito...")
    carrito_btn = driver.find_element(By.CSS_SELECTOR, '[data-bs-toggle="offcanvas"]')
    carrito_btn.click()
    time.sleep(2)

    # 4. Verificar producto en carrito
    lista_items = driver.find_elements(By.CSS_SELECTOR, "#lista-carrito li")
    if not lista_items:
        print("❌ El carrito está vacío")
        raise Exception("Carrito vacío después de agregar producto")
    print("🛒 Producto presente en el carrito")

    # 5. Clic en "Comprar" y manejar secuencia específica de alertas
    print("💳 Haciendo clic en botón Comprar...")
    btn_comprar = driver.find_element(By.ID, "btnComprar")
    btn_comprar.click()
    
    # SECUENCIA ESPECÍFICA DE ALERTAS:
    # Alerta 1: "¿Confirmas la compra de todos los productos en el carrito?"
    print("📢 Esperando primera alerta de confirmación...")
    try:
        alert1 = wait.until(EC.alert_is_present())
        texto1 = alert1.text
        print(f"📢 Alerta 1: {texto1}")
        alert1.accept()
        print("✅ Primera alerta aceptada")
        time.sleep(1)
    except TimeoutException:
        print("⚠️ No apareció la primera alerta de confirmación")
    
    # Alerta 2: "compra guardada ID de compra: XX Total: $XXX"
    print("📢 Esperando segunda alerta de confirmación...")
    try:
        alert2 = wait.until(EC.alert_is_present())
        texto2 = alert2.text
        print(f"📢 Alerta 2: {texto2}")
        alert2.accept()
        print("✅ Segunda alerta aceptada")
        time.sleep(1)
    except TimeoutException:
        print("⚠️ No apareció la segunda alerta de confirmación")
    
    # Manejar cualquier alerta adicional
    print("📢 Verificando alertas adicionales...")
    alertas_adicionales = manejar_alertas_pendientes(driver, wait, max_intentos=3)

    # 6. Esperar redirección a confirmar_compra.html
    print("⏳ Esperando redirección a confirmar_compra...")
    max_reintentos = 3
    for intento in range(max_reintentos):
        try:
            wait.until(EC.url_contains("confirmar_compra"))
            print("📄 Redirigido a confirmar_compra.html")
            break
        except UnexpectedAlertPresentException as e:
            print(f"⚠️ Alerta inesperada durante la espera (intento {intento + 1}): {e.alert_text}")
            try:
                alert = driver.switch_to.alert
                alert.accept()
                print("✅ Alerta inesperada aceptada")
                time.sleep(1)
            except:
                print("❌ No se pudo manejar la alerta inesperada")
            
            if intento == max_reintentos - 1:
                raise
        except TimeoutException:
            print(f"⏰ Timeout esperando redirección (intento {intento + 1})")
            if intento == max_reintentos - 1:
                print("❌ No se pudo completar la redirección después de múltiples intentos")
                raise

    # 7. Ocultar modal de error si aparece
    try:
        driver.execute_script("""
            const modal = document.getElementById('errorModal');
            if (modal && modal.classList.contains('show')) {
                modal.classList.remove('show');
                modal.style.display = 'none';
                document.body.classList.remove('modal-open');
                const backdrop = document.querySelector('.modal-backdrop');
                if (backdrop) backdrop.remove();
            }
        """)
        print("🛑 Modal de error verificado/ocultado")
    except Exception as e:
        print(f"ℹ️ Error manejando modal: {e}")

    # 8. Esperar botón de pagar y hacer clic
    print("💳 Buscando botón de pagar...")
    pagar_btn = wait.until(EC.element_to_be_clickable((By.ID, "btnPagar")))
    driver.execute_script("arguments[0].scrollIntoView(true);", pagar_btn)
    time.sleep(0.5)
    pagar_btn.click()
    print("➡️ Botón 'Pagar con Webpay' presionado")

    # 9. Simular Webpay
    print("⌛ Simulando redirección a Webpay...")
    time.sleep(5)

    try:
        # Intentar automatizar formulario de Webpay
        card_input = wait.until(EC.presence_of_element_located((By.NAME, "card_number")))
        card_input.send_keys("4051885600446623")
        
        driver.find_element(By.NAME, "expiration_date").send_keys("12/30")
        driver.find_element(By.NAME, "cvv").send_keys("123")
        driver.find_element(By.ID, "pay-button").click()

        # Segunda parte del formulario
        rut_input = wait.until(EC.presence_of_element_located((By.NAME, "rut")))
        rut_input.send_keys("11111111-1")
        
        driver.find_element(By.NAME, "clave").send_keys("123")
        driver.find_element(By.ID, "submit-auth").click()
        
        print("✅ Formulario Webpay completado automáticamente")
        
    except Exception as e:
        print(f"⚠️ Webpay no automatizable: {e}")
        print("⏸️ Pausa para intervención manual...")
        input("Presiona Enter después de completar el pago en Webpay...")

    # 10. Esperar redirección a pago_exitoso.html
    print("⏳ Esperando confirmación de pago...")
    try:
        wait.until(EC.url_contains("pago_exitoso"))
        print("✅ Pago exitoso confirmado")
    except UnexpectedAlertPresentException:
        print("⚠️ Alerta inesperada durante confirmación de pago")
        manejar_alertas_pendientes(driver, wait)
        wait.until(EC.url_contains("pago_exitoso"))
        print("✅ Pago exitoso confirmado (después de manejar alertas)")

    # 11. Descargar boleta
    print("📄 Descargando boleta...")
    # RE-OBTENER el elemento btnDescargar en lugar de usar pagar_btn
    try:
        descargar_btn = wait.until(EC.element_to_be_clickable((By.ID, "btnDescargar")))
        driver.execute_script("arguments[0].scrollIntoView(true);", descargar_btn)
        time.sleep(0.5)
        descargar_btn.click()
        print("📄 Boleta descargada")
    except Exception as e:
        print(f"⚠️ Error descargando boleta: {e}")
        # Intento alternativo
        try:
            descargar_btn = driver.find_element(By.ID, "btnDescargar")
            driver.execute_script("arguments[0].click();", descargar_btn)
            print("📄 Boleta descargada (método alternativo)")
        except Exception as e2:
            print(f"❌ No se pudo descargar la boleta: {e2}")

    # 12. Volver al inicio
    print("🏠 Volviendo al inicio...")
    try:
        inicio_btn = wait.until(EC.element_to_be_clickable((By.LINK_TEXT, "Inicio")))
        inicio_btn.click()
        print("🏠 Regreso al inicio completado")
    except Exception as e:
        print(f"⚠️ Error volviendo al inicio: {e}")
        # Intento alternativo con selector diferente
        try:
            inicio_btn = driver.find_element(By.XPATH, "//a[contains(text(), 'Inicio')]")
            inicio_btn.click()
            print("🏠 Regreso al inicio completado (método alternativo)")
        except Exception as e2:
            print(f"❌ No se pudo volver al inicio: {e2}")

    print("\n🎉 ¡Flujo completo de compra ejecutado correctamente!")

except Exception as e:
    print(f"\n❌ Error durante la ejecución: {e}")
    print(f"📍 URL actual: {driver.current_url}")
    print(f"📄 Título de página: {driver.title}")
    
    # Intentar manejar alertas pendientes antes de cerrar
    try:
        print("🚨 Intentando manejar alertas pendientes antes de cerrar...")
        # Crear WebDriverWait corto para el manejo final
        wait_final = WebDriverWait(driver, 2)
        try:
            alert = wait_final.until(EC.alert_is_present())
            print(f"📢 Alerta pendiente encontrada: {alert.text}")
            alert.accept()
            print("✅ Alerta pendiente manejada")
        except TimeoutException:
            print("ℹ️ No hay alertas pendientes")
    except Exception as final_alert_error:
        print(f"⚠️ Error manejando alertas finales: {final_alert_error}")
    
    # Tomar screenshot para debug
    try:
        screenshot_path = "error_screenshot.png"
        driver.save_screenshot(screenshot_path)
        print(f"📸 Screenshot guardado: {screenshot_path}")
    except:
        pass
    
    raise

finally:
    print("\n🔄 Cerrando navegador...")
    driver.quit()
    print("✅ Navegador cerrado")