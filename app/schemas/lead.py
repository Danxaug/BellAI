import re
from pydantic import BaseModel, Field, field_validator

# Expresión regular para validar teléfonos (acepta + opcional y 10-15 dígitos)
PHONE_RE = re.compile(r"^\+?\d{10,15}$")

class LeadRequest(BaseModel):
    """
    Esquema de validación para el formulario de leads.
    Campos obligatorios: nombre, whatsapp, servicio.
    Campo opcional: empresa.
    """
    nombre: str = Field(..., min_length=2, max_length=120, description="Nombre completo del cliente")
    empresa: str = Field(default="", max_length=120, description="Nombre de la empresa (opcional)")
    whatsapp: str = Field(..., min_length=10, max_length=20, description="Número de WhatsApp con código de país")
    servicio: str = Field(..., max_length=64, description="Servicio seleccionado (ej: BellAI Flow, Core, Guard)")

    @field_validator("whatsapp")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        """Limpia y valida el formato del número telefónico."""
        if not v:
            raise ValueError("El número de WhatsApp es obligatorio")
        # Eliminar espacios, guiones y paréntesis
        v_clean = re.sub(r"[\s\-()]", "", v)
        if not PHONE_RE.match(v_clean):
            raise ValueError("Formato de WhatsApp inválido. Use solo números con código de país (ej: 573001234567)")
        return v_clean

    @field_validator("nombre", "empresa", "servicio")
    @classmethod
    def strip_and_sanitize(cls, v: str) -> str:
        """Elimina espacios extra y previene inyección de HTML básica."""
        if not v:
            return v
        if "<" in v or ">" in v:
            raise ValueError("Caracteres no permitidos en el campo")
        return v.strip()

class LeadResponse(BaseModel):
    """Esquema de respuesta para redirigir al usuario a WhatsApp."""
    status: str
    redirect_url: str