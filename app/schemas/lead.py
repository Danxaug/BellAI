import re
from pydantic import BaseModel, Field, field_validator

PHONE_RE = re.compile(r"^\+?\d{10,15}$")

class LeadRequest(BaseModel):
    nombre: str = Field(..., min_length=2, max_length=120)
    empresa: str = Field(default="", max_length=120)
    whatsapp: str = Field(..., min_length=10, max_length=20)
    servicio: str = Field(default="General", max_length=64)

    @field_validator("whatsapp")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        v_clean = re.sub(r"[\s\-()]", "", v)
        if not PHONE_RE.match(v_clean):
            raise ValueError("WhatsApp inválido. Formato: 573001234567")
        return v_clean

    @field_validator("nombre", "empresa", "servicio")
    @classmethod
    def strip_and_no_html(cls, v: str) -> str:
        if "<" in v or ">" in v:
            raise ValueError("Caracteres no permitidos")
        return v.strip()

class LeadResponse(BaseModel):
    status: str
    redirect_url: str