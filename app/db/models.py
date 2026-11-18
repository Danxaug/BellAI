from datetime import datetime, timezone
from sqlalchemy import String, DateTime, func, Index
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Lead(Base):
    __tablename__ = "leads"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    tenant_id: Mapped[str] = mapped_column(String(64), default="bellia", index=True)
    nombre: Mapped[str] = mapped_column(String(120))
    empresa: Mapped[str] = mapped_column(String(120), default="")
    whatsapp: Mapped[str] = mapped_column(String(32), index=True)
    servicio: Mapped[str] = mapped_column(String(64), default="General")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    __table_args__ = (
        Index("ix_leads_whatsapp_tenant", "whatsapp", "tenant_id", unique=True),
    )