import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

# Carga las variables definidas en .env
load_dotenv()

CADENA_CONEXION = (
    f"mysql+pymysql://{os.getenv('BD_USUARIO')}:"
    f"{os.getenv('BD_CONTRASENA')}@"
    f"{os.getenv('BD_SERVIDOR')}:{os.getenv('BD_PUERTO')}/"
    f"{os.getenv('BD_NOMBRE')}?charset=utf8mb4"
)

# Motor y sesión de SQLAlchemy
motor = create_engine(CADENA_CONEXION, echo=True, pool_pre_ping=True)
SesionLocal = sessionmaker(autocommit=False, autoflush=False, bind=motor)
Base = declarative_base()
