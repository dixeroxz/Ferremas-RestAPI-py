import os
from fastapi import Depends, HTTPException, status
from fastapi.security.api_key import APIKeyHeader

# Cabecera esperada
api_key_header = APIKeyHeader(name="X-API-KEY", auto_error=False)

def validar_api_key_general(api_key: str = Depends(api_key_header)) -> str:
    """
    Acepta clave interna o externa.
    Devuelve 'interna' o 'externa'.
    """
    if api_key == os.getenv("API_KEY_INTERNA"):
        return "interna"
    if api_key == os.getenv("API_KEY_EXTERNA"):
        return "externa"
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="API key inválida"
    )

def validar_api_key_interna(api_key: str = Depends(api_key_header)) -> str:
    """
    Sólo acepta clave interna.
    """
    if api_key == os.getenv("API_KEY_INTERNA"):
        return "interna"
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Acceso denegado: sólo clave interna"
    )
