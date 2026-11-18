import urllib.parse
from fastapi import APIRouter, Depends, Request
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.logging import get_logger
from app.db.session import get_db
from app.schemas.lead import LeadRequest, LeadResponse
from app.services.leads import create_or_get_lead

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)
logger = get_logger("leads")
settings = get_settings()


@router.post("/procesar_lead", response_model=LeadResponse)
@limiter.limit("5/minute")
async def procesar_lead(
    request: Request,
    payload: LeadRequest,
    db: AsyncSession = Depends(get_db),
):
    request_id = getattr(request.state, "request_id", "n/a")
    lead = await create_or_get_lead(db, payload)

    logger.info(
        "lead_saved",
        request_id=request_id,
        lead_id=lead.id,
        servicio=lead.servicio,
    )

    msg = (
        f"Hola Bellia! Soy {lead.nombre} de {lead.empresa}. "
        f"Me interesa el servicio de {lead.servicio} y solicito mi diagnóstico gratuito."
    )
    encoded = urllib.parse.quote(msg)
    url = f"https://api.whatsapp.com/send?phone={settings.WHATSAPP_PHONE}&text={encoded}"

    return LeadResponse(status="ok", redirect_url=url)