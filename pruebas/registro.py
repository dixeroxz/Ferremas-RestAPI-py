from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import time

def test_registro():
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)

    # Cambia esta ruta a la ubicación real de tu archivo registro.html
    ruta_html = "file:///C:/Users/alexa.NEJO/Downloads/Ferremas-RestAPI-py/static/registro.html"
    # Abre el archivo HTML
    driver.get(ruta_html)

    # Llena los campos
    driver.find_element(By.ID, "nombre").send_keys("Juan Pépe")
    driver.find_element(By.ID, "correo").send_keys("juan.pep6@example.com")
    driver.find_element(By.ID, "contrasena").send_keys("12345678")
    driver.find_element(By.ID, "direccion").send_keys("Calle Falsa 123")
    driver.find_element(By.ID, "telefono").send_keys("123456789")

    # Envía el formulario
    driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

    # Espera unos segundos para ver la reacción (puedes ajustar)
    time.sleep(5)

    # Cierra el navegador
    driver.quit()

if __name__ == "__main__":
    test_registro()
