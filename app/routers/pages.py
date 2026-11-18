from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.core.config import get_settings
from app.core.translations import TRANSLATIONS  # <-- Nueva importación para el diccionario

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")
limiter = Limiter(key_func=get_remote_address)
settings = get_settings()


# Función auxiliar para renderizar la página en cualquier idioma
def render_index(request: Request, lang: str = "es"):
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "whatsapp_phone": settings.WHATSAPP_PHONE,
            "lang": lang,                                    # Para la etiqueta <html lang="...">
            "t": TRANSLATIONS.get(lang, TRANSLATIONS["es"])  # El diccionario con los textos
        },
    )


@router.get("/", response_class=HTMLResponse)
@limiter.limit("60/minute")
async def read_root(request: Request):
    # Mantenemos exactamente tu misma lógica, solo que ahora usa la función auxiliar en español
    return render_index(request, lang="es")


# NUEVA RUTA PARA INGLÉS
@router.get("/en", response_class=HTMLResponse)
@limiter.limit("60/minute")
async def read_root_en(request: Request):
    # Misma lógica, pero inyectando el idioma inglés
    return render_index(request, lang="en")


@router.get("/privacidad", response_class=HTMLResponse)
@limiter.limit("30/minute")
async def privacy(request: Request):
    return templates.TemplateResponse("privacy.html", {"request": request})