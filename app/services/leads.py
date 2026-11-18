from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import Lead
from app.schemas.lead import LeadRequest

async def create_or_get_lead(db: AsyncSession, data: LeadRequest, tenant_id: str = "bellia") -> Lead:
    existing = await db.execute(select(Lead).where(Lead.whatsapp == data.whatsapp, Lead.tenant_id == tenant_id))
    lead = existing.scalar_one_or_none()
    if lead:
        return lead
    lead = Lead(tenant_id=tenant_id, nombre=data.nombre, empresa=data.empresa, whatsapp=data.whatsapp, servicio=data.servicio)
    db.add(lead)
    try:
        await db.commit()
        await db.refresh(lead)
    except IntegrityError:
        await db.rollback()
        existing = await db.execute(select(Lead).where(Lead.whatsapp == data.whatsapp, Lead.tenant_id == tenant_id))
        lead = existing.scalar_one()
    return lead
