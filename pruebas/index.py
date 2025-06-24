from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time
import json

# Configura tu WebDriver
chrome_options = Options()
chrome_options.add_argument("--start-maximized")
driver = webdriver.Chrome(service=Service(), options=chrome_options)

try:
    # Cargar la página local
    driver.get("http://127.0.0.1:8000/static/index.html")  # Ajusta si tu HTML está en otro puerto o ruta

    time.sleep(2)

    # Simular un usuario logueado con rol "cliente"
    usuario_simulado = {
        "id": 5,
        "nombre": "Juan Pépe",
        "rol": "cliente",
        "email": "juan.pepe@example.com"
    }
    driver.execute_script(f"localStorage.setItem('usuarioLogueado', '{json.dumps(usuario_simulado)}');")
    print("🔐 Usuario cliente simulado almacenado en localStorage")

    # Refrescar y esperar que detecte al usuario
    driver.refresh()
    time.sleep(2)
    

    # Esperar a que los productos se carguen
    productos = driver.find_elements(By.CLASS_NAME, "agregar-carrito")
    assert len(productos) > 0, "No se cargaron productos"

    # Agregar el primer producto al carrito
    productos[0].click()
    print("✅ Producto agregado al carrito")

    time.sleep(1)

    # Simular un usuario logueado con rol "cliente"

    # Abrir el carrito
    driver.execute_script("document.querySelector('[data-bs-toggle=\"offcanvas\"]').click()")
    time.sleep(2)

    # Verificar que el producto esté en el carrito
    lista_items = driver.find_elements(By.CSS_SELECTOR, "#lista-carrito li")
    assert len(lista_items) > 0, "El carrito está vacío después de agregar el producto"
    print("🛒 Producto encontrado en el carrito")

    # Presionar el botón "Comprar"
    btn_comprar = driver.find_element(By.ID, "btnComprar")
    btn_comprar.click()
    time.sleep(2)

    # Confirmar el diálogo (si se presenta)
    alert = driver.switch_to.alert
    alert.accept()  # Confirmar compra
    print("💳 Compra confirmada en alerta")

    time.sleep(3)

    # Verificar que el carrito fue vaciado
    lista_vacia = driver.find_element(By.ID, "lista-carrito").text
    assert "carrito está vacío" in lista_vacia.lower()
    print("✅ Carrito vaciado tras la compra")

finally:
    driver.quit()
