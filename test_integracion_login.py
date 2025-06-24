import uuid
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_flujo_completo_registro_login_token():
    # Correo único para evitar duplicados
    correo_unico = f"carlos_{uuid.uuid4().hex}@example.com"

    # Paso 1: Registro de usuario
    datos_registro = {
        "nombre": "Carlos Test",
        "correo": correo_unico,
        "contrasena": "test1234",
        "direccion": "Calle Falsa 123",
        "telefono": "123456789"
    }

    resp_registro = client.post("/usuarios", json=datos_registro)
    assert resp_registro.status_code == 200
    data_registro = resp_registro.json()
    assert data_registro["correo"] == correo_unico

    # Paso 2: Login
    datos_login = {
        "correo": correo_unico,
        "contrasena": "test1234"
    }

    resp_login = client.post("/login", json=datos_login)
    assert resp_login.status_code == 200
    data_login = resp_login.json()

    # Validar campos esperados
    assert data_login["correo"] == correo_unico
    assert data_login["nombre"] == "Carlos Test"
    assert data_login["direccion"] == "Calle Falsa 123"
    assert data_login["telefono"] == "123456789"
    assert data_login["rol"] == "cliente"
    assert "id" in data_login
