from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time

# Ruta local al archivo login.html
ruta_login = "file:///C:/Users/alexa.NEJO/Downloads/Ferremas-RestAPI-py/static/login.html"

# Configurar el navegador (usa Chrome en modo visible)
driver = webdriver.Chrome()

try:
    # Abrir la página login.html
    driver.get(ruta_login)
    time.sleep(1)

    # Completar campos
    email_input = driver.find_element(By.ID, "email")
    password_input = driver.find_element(By.ID, "password")
    remember_checkbox = driver.find_element(By.ID, "rememberMe")
    submit_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")

    # Datos de prueba
    email_input.send_keys("juan.pep6@example.com")
    password_input.send_keys("12345678")
    remember_checkbox.click()
    time.sleep(0.5)

    # Enviar el formulario
    submit_button.click()

    # Esperar la respuesta simulada (alerta, redirección, etc.)
    time.sleep(3)

    # Capturar y mostrar el mensaje de alerta (si aparece)
    try:
        alert = driver.find_element(By.CLASS_NAME, "alert")
        print("🟢 Mensaje mostrado:", alert.text)
    except:
        print("⚠️ No se encontró ningún mensaje de alerta.")

finally:
    # Cerrar navegador
    time.sleep(2)
    driver.quit()
