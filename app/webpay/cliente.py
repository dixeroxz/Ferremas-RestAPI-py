import os
from transbank.webpay.webpay_plus.transaction import Transaction
from transbank.common.integration_type import IntegrationType

# Cargar variables de entorno o valores por defecto para pruebas
commerce_code = os.getenv("WEBPAY_COMMERCE_CODE", "597055555532")  # código de comercio de integración
api_key = os.getenv("WEBPAY_API_KEY", "597055555532")              # api_key de integración
env = os.getenv("WEBPAY_ENVIRONMENT", "integration").lower()

# Determinar tipo de integración
integration_type = (
    IntegrationType.TEST if env == "integration" else IntegrationType.LIVE
)

# Instanciar transacción con configuración correcta
webpay_transaction = Transaction(
    commerce_code=commerce_code,
    api_key=api_key,
    integration_type=integration_type
)
 