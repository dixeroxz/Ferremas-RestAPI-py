from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter()

templates = Jinja2Templates(directory="app/templates")

@router.get("/pagos/redireccionar/{token}", response_class=HTMLResponse)
def redireccion_webpay(request: Request, token: str):
    return templates.TemplateResponse(
        "redireccion_webpay.html",
        {
            "request": request,
            "token": token,
            "url_redireccion": "https://webpay3gint.transbank.cl/webpayserver/initTransaction"
        }
    )