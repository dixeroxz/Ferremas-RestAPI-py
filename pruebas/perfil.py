from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import json

# Configuración
options = Options()
options.add_argument("--start-maximized")

# Ruta local del archivo HTML
ruta_local = "file:///C:/Users/alexa.NEJO/Downloads/Ferremas-RestAPI-py/static/perfil.html"

# Datos del usuario
usuario = {
    "id": 5,
    "nombre": "Juan Pépe",
    "correo": "juan.pepe@example.com",
    "rol": "cliente",
    "direccion": "Calle Falsa 123",
    "telefono": "987654321"
}

# Iniciar navegador
driver = webdriver.Chrome(options=options)
wait = WebDriverWait(driver, 15)

# Simular login
driver.get("about:blank")
driver.execute_script(f"localStorage.setItem('usuarioLogueado', '{json.dumps(usuario)}');")

# Abrir perfil
driver.get(ruta_local)

# Esperar a que cargue el formulario
wait.until(EC.presence_of_element_located((By.ID, "nombre")))

# Completar campos
driver.find_element(By.ID, "nombre").clear()
driver.find_element(By.ID, "nombre").send_keys("Juan Carlos Pépe")

driver.find_element(By.ID, "direccion").clear()
driver.find_element(By.ID, "direccion").send_keys("Av. Siempre Viva 742")

driver.find_element(By.ID, "telefono").clear()
driver.find_element(By.ID, "telefono").send_keys("987654321")

# Enviar formulario
driver.find_element(By.CSS_SELECTOR, "form#formPerfil button[type='submit']").click()

# Esperar alerta de éxito o error
try:
    alerta = wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "alert")))
    print("✅ Alerta mostrada:", alerta.text)
except:
    print("❌ No se encontró alerta tras enviar el formulario.")

# Esperar a que se cargue el historial de compras
try:
    compras_container = wait.until(EC.visibility_of_element_located((By.ID, "comprasContainer")))
    print("📦 Historial de compras cargado.")
except:
    print("🛒 No se encontró historial de compras.")
    driver.quit()
    exit()

# Buscar botón de descarga de boleta
try:
    boton_boleta = driver.find_element(By.CSS_SELECTOR, "#tablaCompras button.btn-success")
    boton_boleta.click()
    print("📄 Se hizo clic en el botón de descarga de boleta.")
    time.sleep(3)  # Dar tiempo para que el PDF se genere
except:
    print("❌ No se encontró botón de descarga de boleta.")

# Finalizar
driver.quit()
