import re
import json
import os
import urllib.parse
from datetime import datetime
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field, field_validator

router = APIRouter()

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

# --- Funciones Auxiliares de Guardado (Core del Sistema) ---

def save_data(data: dict):
    """Función centralizada para escribir en el JSON de leads."""
    file_path = "app/data/leads_capturados.json"
    
    # Asegurar que la carpeta exista
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    # Leer leads existentes o iniciar lista vacía
    leads = []
    if os.path.exists(file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                leads = json.load(f)
        except Exception:
            leads = []
    
    # Agregar nuevo lead
    leads.append(data)
    
    # Sobrescribir archivo con todos los leads (incluido el nuevo)
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(leads, f, indent=4, ensure_ascii=False)
        
    print(f"✅ LEAD GUARDADO EN DISCO: {data.get('nombre')} - {data.get('telefono')}")

def guardar_lead_en_archivo(lead: LeadRequest):
    """Guarda un lead validado desde formulario web."""
    save_data({
        "nombre": lead.nombre,
        "empresa": lead.empresa,
        "telefono": lead.whatsapp,
        "servicio": lead.servicio,
        "fuente": "Formulario Web",
        "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })

def guardar_lead_en_archivo_simple(data: dict):
    """Guarda datos crudos provenientes del chatbot."""
    save_data(data)

# --- Endpoints de la API ---

@router.post("/procesar_lead", response_model=LeadResponse)
async def procesar_lead(lead: LeadRequest):
    # 1. Guardar en archivo JSON (Persistencia inmediata)
    guardar_lead_en_archivo(lead)
    
    # 2. Generar mensaje y URL para WhatsApp
    phone_clean = re.sub(r"[\s\-()]", "", lead.whatsapp)
    msg = f"Hola BellAI, soy {lead.nombre} de {lead.empresa}. Me interesa el servicio: {lead.servicio}."
    encoded_msg = urllib.parse.quote(msg)
    redirect_url = f"https://api.whatsapp.com/send?phone={phone_clean}&text={encoded_msg}"
    
    return LeadResponse(status="success", redirect_url=redirect_url)

@router.post("/guardar-lead-chat")
async def guardar_lead_chat(nombre: str, empresa: str, telefono: str, sector: str = "", necesidad: str = ""):
    """
    Recibe datos del chatbot y los guarda sin redirigir.
    Valida que los datos sean mínimos necesarios.
    """
    if not nombre or not telefono:
        raise HTTPException(status_code=400, detail="Faltan datos obligatorios (Nombre o Teléfono)")
    
    lead_data = {
        "nombre": nombre.strip(),
        "empresa": empresa.strip() if empresa else "No especificada",
        "telefono": telefono.strip(),
        "sector": sector.strip() if sector else "General",
        "necesidad": necesidad.strip() if necesidad else "Interés general",
        "fuente": "Chatbot IA",
        "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    guardar_lead_en_archivo_simple(lead_data)
    
    return {"status": "success", "message": f"Lead de {nombre} guardado correctamente desde Chat"}