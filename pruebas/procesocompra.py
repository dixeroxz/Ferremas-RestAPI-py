from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, UnexpectedAlertPresentException, NoSuchElementException
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

def automatizar_webpay(driver, wait):
    """Función específica para automatizar el flujo completo de Webpay"""
    print("💳 Iniciando automatización de Webpay...")
    
    try:
        # Paso 1: Seleccionar método de pago "Tarjetas" - ACTUALIZADO CON EL HTML CORRECTO
        print("🔍 Buscando botón 'Tarjetas' con selectores específicos de Angular...")
        
        # Selectores actualizados basados en el HTML real de Webpay/Transbank
        selectores_tarjetas = [
            # Selector específico por ID
            "#tarjetas",
            "button#tarjetas",
            # Selector por atributo app-payment-buttom
            "button[app-payment-buttom]",
            "button[app-payment-buttom][id='tarjetas']",
            # Selector por clase y contenido
            ".payment-options__method-items-option",
            "button.payment-options__method-items-option",
            # Selector combinado más específico
            "button.payment-options__method-items-option#tarjetas",
            # Selector por texto dentro del botón
            "//button[@id='tarjetas']",
            "//button[contains(@class, 'payment-options__method-items-option') and @id='tarjetas']",
            "//button[@app-payment-buttom and @id='tarjetas']",
            # Selectores por contenido de texto
            "//button[contains(.//div, 'Tarjetas')]",
            "//button[contains(.//div[@class='method-item-option-type'], 'Tarjetas')]",
            # Selector por span interno
            "//button[contains(.//span, 'Crédito, Débito, Prepago')]",
            # Selectores más generales como fallback
            "//button[contains(text(), 'Tarjetas')]",
            "//button[contains(text(), 'tarjetas')]",
            "//button[contains(text(), 'TARJETAS')]"
        ]
        
        boton_tarjetas = None
        selector_usado = None
        
        # Esperar a que la página de Webpay cargue completamente
        print("⏳ Esperando que la página de Webpay cargue...")
        time.sleep(3)
        
        for selector in selectores_tarjetas:
            try:
                print(f"🔍 Probando selector: {selector}")
                if selector.startswith("//"):
                    boton_tarjetas = wait.until(EC.element_to_be_clickable((By.XPATH, selector)))
                else:
                    boton_tarjetas = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
                selector_usado = selector
                print(f"✅ Botón 'Tarjetas' encontrado con selector: {selector}")
                break
            except TimeoutException:
                print(f"❌ Selector falló: {selector}")
                continue
        
        if not boton_tarjetas:
            print("⚠️ No se encontró el botón 'Tarjetas', mostrando información de debug...")
            
            # Debug mejorado: mostrar estructura de la página
            try:
                print("📋 Estructura de botones disponibles:")
                botones = driver.find_elements(By.TAG_NAME, "button")
                for i, btn in enumerate(botones[:15]):  # Limitar a 15 botones
                    try:
                        text = btn.text.strip()[:50] if btn.text else "Sin texto"
                        classes = btn.get_attribute("class") or "Sin clases"
                        id_attr = btn.get_attribute("id") or "Sin ID"
                        print(f"  Botón {i+1}: ID='{id_attr}', Class='{classes[:50]}...', Text='{text}'")
                    except:
                        continue
                
                # Buscar elementos con las clases específicas
                print("🔍 Buscando elementos con clases payment-options:")
                payment_elements = driver.find_elements(By.CSS_SELECTOR, "[class*='payment-options']")
                for elem in payment_elements:
                    try:
                        print(f"  Elemento: {elem.tag_name}, Class: {elem.get_attribute('class')}, Text: {elem.text[:30]}")
                    except:
                        continue
                        
            except Exception as debug_error:
                print(f"Error en debug: {debug_error}")
            
            raise Exception("No se encontró el botón 'Tarjetas' con ningún selector")
        
        # Hacer scroll al elemento y hacer clic
        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", boton_tarjetas)
        time.sleep(1)
        
        # Intentar clic normal primero, luego JavaScript si falla
        try:
            boton_tarjetas.click()
        except Exception as click_error:
            print(f"⚠️ Clic normal falló, usando JavaScript: {click_error}")
            driver.execute_script("arguments[0].click();", boton_tarjetas)
        
        print(f"✅ Método de pago 'Tarjetas' seleccionado usando: {selector_usado}")
        time.sleep(3)  # Tiempo extra para que la página procese la selección
        
        # Paso 2: Ingresar número de tarjeta
        print("💳 Ingresando número de tarjeta...")
        selectores_tarjeta = [
            "input[id*='card']",
            ".card-number-input",
            "input[type='text'][maxlength='19']",  # Común para números de tarjeta
            "input[autocomplete='cc-number']",
            "//input[contains(@placeholder, 'tarjeta')]",
            "//input[contains(@placeholder, 'Tarjeta')]",
            "//input[contains(@placeholder, 'Número')]"
        ]
        
        campo_tarjeta = None
        for selector in selectores_tarjeta:
            try:
                if selector.startswith("//"):
                    campo_tarjeta = wait.until(EC.presence_of_element_located((By.XPATH, selector)))
                else:
                    campo_tarjeta = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
                print(f"✅ Campo de tarjeta encontrado con: {selector}")
                break
            except TimeoutException:
                continue
        
        if not campo_tarjeta:
            # Debug para campos de input
            print("🔍 Campos de input disponibles:")
            inputs = driver.find_elements(By.TAG_NAME, "input")
            for i, inp in enumerate(inputs[:10]):
                try:
                    placeholder = inp.get_attribute("placeholder") or "Sin placeholder"
                    name = inp.get_attribute("name") or "Sin name"
                    id_attr = inp.get_attribute("id") or "Sin ID"
                    input_type = inp.get_attribute("type") or "Sin type"
                    print(f"  Input {i+1}: ID='{id_attr}', Name='{name}', Type='{input_type}', Placeholder='{placeholder}'")
                except:
                    continue
            raise Exception("No se encontró el campo de número de tarjeta")
        
        # Enfocar el campo y limpiar antes de escribir
        driver.execute_script("arguments[0].focus();", campo_tarjeta)
        campo_tarjeta.clear()
        time.sleep(0.5)
        campo_tarjeta.send_keys("4051885600446623")
        print("✅ Número de tarjeta ingresado")
        time.sleep(2)
        
        
        
        # Paso 4: Ingresar fecha de expiración
        print("📅 Ingresando fecha de expiración...")
        selectores_fecha = [
            "input[formcontrolname='fechaExpiracion']",  # Muy específico para Angular
            "input[id='card-exp']",                      # ID exacto
            "input[appformatexpirationdate]",            # Directiva Angular específica
            "input.card-input[placeholder*='MM/AA']"    # Combinando clase y placeholder
        ]
        
        campo_fecha = None
        for selector in selectores_fecha:
            try:
                if selector.startswith("//"):
                    campo_fecha = wait.until(EC.presence_of_element_located((By.XPATH, selector)))
                else:
                    campo_fecha = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
                break
            except TimeoutException:
                continue
        
        if not campo_fecha:
            raise Exception("No se encontró el campo de fecha de expiración")
        
        campo_fecha.clear()
        campo_fecha.send_keys("1230")  # Sin el /
        print("✅ Fecha de expiración ingresada")
        time.sleep(2)
        
        # Paso 5: Ingresar CVV
        print("🔒 Ingresando CVV...")
        selectores_cvv = [
          "input[formcontrolname='cvv']",        # Muy específico para Angular
          "input[id='card-cvv']",                # ID exacto
          "input[appformatcvvnumber]",           # Directiva Angular específica
          "input[placeholder='•••']",            # Placeholder específico de puntos
          "input[maxlength='3'][type='password']", # Combinación común para CVV
          "input[aria-describedby*='cvv']"  
        ]
        
        campo_cvv = None
        for selector in selectores_cvv:
            try:
                if selector.startswith("//"):
                    campo_cvv = wait.until(EC.presence_of_element_located((By.XPATH, selector)))
                else:
                    campo_cvv = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
                break
            except TimeoutException:
                continue
        
        if not campo_cvv:
            raise Exception("No se encontró el campo CVV")
        
        campo_cvv.clear()
        campo_cvv.send_keys("123")
        print("✅ CVV ingresado")
        time.sleep(2)
        
        # Paso 6: Scroll hacia abajo antes del segundo continuar
        print("📜 Scrolleando hacia abajo...")
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1)
        
        
        # Paso 7: Presionar botón "Pagar"
        print("💰 Presionando botón 'Pagar'...")
        selectores_pagar = [
            "//button[contains(text(), 'Pagar')]",
            "//button[contains(text(), 'PAGAR')]",
            "//button[contains(text(), 'pagar')]",
            "//button[contains(text(), 'Confirmar')]",
            "//button[contains(text(), 'CONFIRMAR')]",
            "#pay-button",
            "#pagar-btn",
            "#confirmar-btn",
            ".pay-button",
            ".btn-pay",
            "button[type='submit']",
            "input[type='submit'][value*='Pagar']"
        ]
        
        boton_pagar = None
        for selector in selectores_pagar:
            try:
                if selector.startswith("//"):
                    boton_pagar = wait.until(EC.element_to_be_clickable((By.XPATH, selector)))
                else:
                    boton_pagar = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
                break
            except TimeoutException:
                continue
        
        if not boton_pagar:
            raise Exception("No se encontró el botón 'Pagar'")
        
        boton_pagar.click()
        print("✅ Botón 'Pagar' presionado")
        time.sleep(5)  # Tiempo extra para la transición
        
        # Paso 9: Segunda página - Ingresar RUT y clave
        print("🆔 Ingresando RUT y clave en segunda página...")
        
        # Ingresar RUT
        selectores_rut = [
            # Por atributo name (más común)
            "input[name*='rut']",
            "input[name*='RUT']",
            "input[name='rut']",
            "input[name='rutClient']",
            "input[name='rutCliente']",
            "input[name='usuario']",

            # Por atributo id
            "input[id*='rut']",
            "input[id*='RUT']",
            "input[id='rut']",
            "input[id='rutClient']",
            "input[id='rutCliente']",

            # Por placeholder
            "input[placeholder*='RUT']",
            "input[placeholder*='rut']",
            "input[placeholder*='R.U.T']",
            "input[placeholder*='Rut']",
            "input[placeholder*='usuario']",

            # Por clases CSS
            ".rut-input",
            ".rut",
            ".usuario-input",

            # XPath más genéricos
            "//input[contains(@name, 'rut')]",
            "//input[contains(@id, 'rut')]",
            "//input[contains(@placeholder, 'RUT')]",
            "//input[contains(@placeholder, 'rut')]",
            "//input[contains(@class, 'rut')]",

            # Selectores más generales (como fallback)
            "input[type='text']:first-of-type",
            "form input[type='text']:first-child"
        ]
        
        campo_rut = None
        for selector in selectores_rut:
            try:
                if selector.startswith("//"):
                    campo_rut = wait.until(EC.presence_of_element_located((By.XPATH, selector)))
                else:
                    campo_rut = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
                break
            except TimeoutException:
                continue
        
        if not campo_rut:
            raise Exception("No se encontró el campo RUT")
        
        campo_rut.clear()
        campo_rut.send_keys("11.111.111-1")
        print("✅ RUT ingresado")
        time.sleep(1)
        
        # Ingresar clave
        selectores_clave = [

            "input[type='password']",
            "input[id*='password']",
            "input[id*='pin']",
            ".password-input",
            ".clave-input",
            "//input[contains(@placeholder, 'clave')]",
            "//input[contains(@placeholder, 'Clave')]"
        ]
        
        campo_clave = None
        for selector in selectores_clave:
            try:
                if selector.startswith("//"):
                    campo_clave = wait.until(EC.presence_of_element_located((By.XPATH, selector)))
                else:
                    campo_clave = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
                break
            except TimeoutException:
                continue
        
        if not campo_clave:
            raise Exception("No se encontró el campo clave")
        
        campo_clave.clear()
        campo_clave.send_keys("123")
        print("✅ Clave ingresada")
        time.sleep(1)
        
       # Paso 10: Presionar "Aceptar" (primera página)
        print("✅ Presionando 'Aceptar'...")
        selectores_aceptar = [
        "input[type='submit']",
        "input[value='Aceptar']",
        "input[value*='Aceptar']",
        "//input[@value='Aceptar']",
        "//input[contains(@value, 'Aceptar')]",
        "//input[contains(@value, 'ACEPTAR')]",
        "//input[contains(@value, 'Confirmar')]",
        "//button[contains(text(), 'Aceptar')]",
        "button[type='submit']",
        "#submit-auth",
        "#aceptar-btn"
      ]

        boton_aceptar = None
        for selector in selectores_aceptar:
         try:
            if selector.startswith("//"):
                boton_aceptar = wait.until(EC.element_to_be_clickable((By.XPATH, selector)))
            else:
                boton_aceptar = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
            break
         except TimeoutException:
            continue

        if not boton_aceptar:
         raise Exception("No se encontró el botón 'Aceptar'")

        boton_aceptar.click()
        print("✅ Botón 'Aceptar' presionado")
        time.sleep(3)  # Reducido para ser más eficiente

      # Paso 11: Segunda página - Presionar "Continuar"
        print("🎯 Procesando página de confirmación - Buscando 'Continuar'...")
        try:
           selectores_continuar = [
            "input[type='submit']",
            "input[value='Continuar']",
            "input[value='CONTINUAR']",
            "input[value*='Continuar']",
            "input[value*='CONTINUAR']",
            "input[value='Aceptar']",
            "input[value='Confirmar']",
            "//input[@value='Continuar']",
            "//input[contains(@value, 'Continuar')]",
            "//input[contains(@value, 'CONTINUAR')]",
            "button[type='submit']",
            "//button[contains(text(), 'Continuar')]",
            "#continuar-btn",
            "#submit-btn"
           ]

           boton_continuar = None
           for selector in selectores_continuar:
            try:
                if selector.startswith("//"):
                    boton_continuar = wait.until(EC.element_to_be_clickable((By.XPATH, selector)))
                else:
                    boton_continuar = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
                print(f"✅ Encontrado botón 'Continuar' con selector: {selector}")
                break
            except TimeoutException:
                continue

           if boton_continuar:
            boton_continuar.click()
            print("✅ Botón 'Continuar' presionado")
            time.sleep(3)

            # Paso 12: Esperar redirección a página de pago exitoso
            print("🎯 Esperando redirección a página de pago exitoso...")

            try:
                wait.until(lambda driver: "exitoso" in driver.page_source.lower() or
                                      "éxito" in driver.page_source.lower() or
                                      "aprobado" in driver.page_source.lower() or
                                      "completado" in driver.page_source.lower())
                print("✅ Pago procesado exitosamente")
            except TimeoutException:
                print("⚠️ No se detectó confirmación de pago exitoso, pero continuando...")

           else:
            print("❌ No se encontró botón 'Continuar' en la página de confirmación")
            driver.save_screenshot("debug_no_continuar.png")

        except Exception as e:
           print(f"❌ Error en paso de confirmación: {str(e)}")
           driver.save_screenshot("debug_error_confirmacion.png")
        
        # Paso 12: Esperar procesamiento de Webpay
        print("⏳ Esperando que Webpay procese el pago...")
        time.sleep(8)  # Tiempo adicional para el procesamiento
        
        print("✅ Automatización de Webpay completada")
        return True
        
    except Exception as e:
        print(f"❌ Error en automatización de Webpay: {e}")
        # Tomar screenshot para debug
        try:
            driver.save_screenshot("webpay_error.png")
            print("📸 Screenshot de error guardado: webpay_error.png")
        except:
            pass
        return False

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

# Configuración de Chrome mejorada para evitar errores de tensores
chrome_options = Options()
chrome_options.add_argument("--start-maximized")
chrome_options.add_argument("--disable-web-security")
chrome_options.add_argument("--disable-features=VizDisplayCompositor")
# Opciones adicionales para resolver problemas de ML/AI
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--disable-software-rasterizer")
chrome_options.add_argument("--disable-background-timer-throttling")
chrome_options.add_argument("--disable-backgrounding-occluded-windows")
chrome_options.add_argument("--disable-renderer-backgrounding")
chrome_options.add_argument("--disable-extensions")
chrome_options.add_argument("--disable-plugins")
chrome_options.add_argument("--disable-default-apps")

driver = webdriver.Chrome(service=Service(), options=chrome_options)
wait = WebDriverWait(driver, 20)  # Aumentado el timeout

# Simular usuario cliente
usuario_simulado = {
    "id": 4,
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

    # 9. Automatizar Webpay con el flujo específico
    print("⌛ Iniciando automatización completa de Webpay...")
    webpay_exitoso = automatizar_webpay(driver, wait)
    
    if not webpay_exitoso:
        print("⚠️ Automatización de Webpay falló, permitiendo intervención manual...")
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