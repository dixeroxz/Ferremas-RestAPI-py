# en test_ferremas.py o un conftest_test.py aparte
import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.base_de_datos import Base

# Este será el motor de pruebas (SQLite en memoria)
DATABASE_URL = "sqlite:///:memory:"
test_engine = create_engine(DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

# Fixture global que limpia y recrea las tablas antes de cada test
@pytest.fixture(autouse=True, scope="function")
def limpiar_db():
    connection = test_engine.connect()
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)
    yield
    connection.close()

@pytest.fixture(scope="function")
def db():
    session = TestingSessionLocal()
    yield session
    session.close()
