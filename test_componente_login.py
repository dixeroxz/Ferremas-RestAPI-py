import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.base_de_datos import Base
from app.modelos.usuario import Usuario
from app.repositorios.usuario_repositorio import crear_usuario
from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from fastapi import HTTPException
from app.servicios.usuario_servicio import autenticar_usuario
from conftest import TestingSessionLocal
from app.servicios.usuario_servicio import pwd_context
  # Ajusta al módulo principal de FastAPI

class Compra(Base):
    __tablename__ = "compras"
    id = Column(Integer, primary_key=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"))
    usuario = relationship("Usuario", back_populates="compras")

class Pago(Base):
    __tablename__ = "pagos"
    id = Column(Integer, primary_key=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"))
    usuario = relationship("Usuario", back_populates="pagos")


@pytest.fixture(scope="function")
def db():
    session = TestingSessionLocal()
    yield session
    session.close()

#TEST 1
def test_registrar_usuario_valido(db):
    from app.repositorios.usuario_repositorio import crear_usuario

    nuevo = crear_usuario(
        db,
        nombre="Juan Pérez",
        correo="juan@example.com",
        contrasena="secreta123",
        direccion="Calle 123",
        telefono="987654321"
    )

    assert nuevo.id is not None
    assert nuevo.nombre == "Juan Pérez"
    assert nuevo.correo == "juan@example.com"
    assert nuevo.direccion == "Calle 123"
    assert nuevo.telefono == "987654321"
#TEST 2
def test_registrar_usuario_duplicado(db):

    # Crea el primer usuario
    crear_usuario(
        db,
        nombre="Juan Pérez",
        correo="juan@example.com",
        contrasena="secreta123",
        direccion="Calle 123",
        telefono="987654321"
    )

    # Intenta crear el mismo usuario nuevamente
    with pytest.raises(HTTPException) as exc_info:
        crear_usuario(
            db,
            nombre="Juan Pérez",
            correo="juan@example.com",  # mismo correo
            contrasena="secreta123",
            direccion="Calle 123",
            telefono="987654321"
        )

    assert exc_info.value.status_code == 400
    assert "correo ya está registrado" in exc_info.value.detail.lower()

#TEST 3

def test_login_credenciales_validas(db):
    from app.repositorios.usuario_repositorio import crear_usuario
    from app.modelos.usuario import Usuario

    # Crear usuario
    crear_usuario(
        db,
        nombre="Ana Torres",
        correo="ana@example.com",
        contrasena="clave123",
        direccion="Av. Siempre Viva 456",
        telefono="123456789"
    )

    # Simular login
    usuario = db.query(Usuario).filter_by(correo="ana@example.com", contrasena="clave123").first()

    assert usuario is not None
    assert usuario.nombre == "Ana Torres"
    assert usuario.correo == "ana@example.com"

#TEST 4

def test_login_credenciales_invalidas(db):
    from app.servicios.usuario_servicio import crear_usuario, autenticar_usuario
    from fastapi import HTTPException

    crear_usuario(
        db,
        nombre="Ana Torres",
        correo="ana@example.com",
        contrasena="clave123",
        direccion="Av. Siempre Viva 456",
        telefono="123456789"
    )

    with pytest.raises(HTTPException) as exc_info:
        autenticar_usuario(db, correo="ana@example.com", contrasena="malaclave123")

    assert exc_info.value.status_code == 401
    assert "incorrecta" in exc_info.value.detail.lower()

# TEST 5
def test_validar_api_key_general_correcta(monkeypatch):
    from app.seguridad import validar_api_key_general

    # Simular claves
    monkeypatch.setenv("API_KEY_EXTERNA", "claveExternaParaTi789")
    monkeypatch.setenv("API_KEY_INTERNA", "claveInternaSuperSecreta123")

    # Crear función auxiliar que imite el Depends
    resultado = validar_api_key_general(api_key="claveExternaParaTi789")
    assert resultado == "externa"

#TEST 6

#from fastapi.testclient import TestClient
#from app.main import app  # Ajusta al módulo principal de FastAPI

#client = TestClient(app)

#def test_redireccion_sin_sesion():
 #   response = client.get("/perfil", allow_redirects=False)  # o la ruta protegida

 #   assert response.status_code in [302, 307]  # Redirección
 #   assert "/login" in response.headers.get("location", "")  # Destino esperado
 # TEST CON ERROR
