# 🛠️ FERREMAS REST API

Este proyecto es una REST API desarrollada con **FastAPI** para la gestión de productos. Aquí encontrarás los pasos necesarios para ejecutar la API localmente y probar sus endpoints mediante Swagger o Postman.

---

## 🚀 Paso a paso para iniciar el proyecto

```bash
# 1. Crear y activar entorno virtual

python -m venv venv

# En Windows PowerShell, permitir ejecución de scripts (solo si es necesario)
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process

# Activar el entorno virtual
.\venv\Scripts\Activate
```

```bash
# 2. Instalar dependencias

pip install -r requirements.txt
```

```bash
# Si faltan algunos módulos, instálalos manualmente con:

pip install cryptography SQLAlchemy python-dotenv bcrypt passlib
```

```bash
# 3. Configurar base de datos MySQL

Desde el cliente de MySQL (puedes abrirlo con mysql -u root -p):

CREATE USER 'ferremas'@'localhost' IDENTIFIED BY 'FerrePass2025!';
CREATE DATABASE mi_base_de_datos;
GRANT ALL PRIVILEGES ON mi_base_de_datos.* TO 'ferremas'@'localhost';
FLUSH PRIVILEGES;

```

```bash
# 4. Ejecutar la API

uvicorn app.main:app --reload
```

```bash
# 5. Probar la API

Accede a la documentación interactiva de Swagger en:
http://127.0.0.1:8000/docs

para la parte de WebPay es necesario entrar con la URL de ngrok que aparece al iniciar el programa+ el token generado en el endpoint de crear pago

O utiliza Postman para probar los endpoints según tu preferencia.
```

```bash
✨ ¡Listo! Ya tienes tu API corriendo localmente y lista para usarse.
```






