# 🛠️ FERREMAS REST API

Este proyecto es una REST API desarrollada con **FastAPI** para la gestión de productos. Aquí encontrarás los pasos necesarios para ejecutar la API localmente y probar sus endpoints mediante Swagger o Postman.

---

## 🚀 Paso a paso para iniciar el proyecto

### 1. Crear y activar entorno virtual

```bash
python -m venv venv


Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
.\venv\Scripts\Activate

---

2. Instalar dependencias

pip install -r requirements.txt

Si faltan algunos módulos, instálalos manualmente:

pip install cryptography SQLAlchemy python-dotenv bcrypt passlib

---

3. Configurar base de datos MySQL
Desde el cliente de MySQL (puedes abrirlo con mysql -u root -p):

CREATE USER 'ferremas'@'localhost' IDENTIFIED BY 'FerrePass2025!';
CREATE DATABASE mi_base_de_datos;
GRANT ALL PRIVILEGES ON mi_base_de_datos.* TO 'ferremas'@'localhost';
FLUSH PRIVILEGES;

---

4. Ejecutar la API
Desde el directorio raíz del proyecto, ejecuta:

uvicorn app.main:app --reload

Esto levantará el servidor en modo desarrollo en http://127.0.0.1:8000.
