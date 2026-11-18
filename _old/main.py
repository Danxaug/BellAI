import os
import sqlite3
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from groq import Groq

load_dotenv()

limiter = Limiter(key_func=get_remote_address)
app = FastAPI(title="Bellia - AI & Tech Agency")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Servir archivos estáticos (imágenes, CSS)
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Inicializar Base de Datos SQLite
def init_db():
    conn = sqlite3.connect("bellia_leads.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS leads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            empresa TEXT,
            whatsapp TEXT NOT NULL,
            servicio TEXT,
            fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

init_db()

# Cliente de Groq para la IA de Bellia
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY", "DUMMY_KEY"))

SYSTEM_PROMPT = """
Eres Bellia AI, el Asesor de Tecnología y Ventas de BELLIA (representado visualmente por un Cyber-Bulldog de inteligencia táctica).
Tu objetivo es atender gerentes, profesionales y dueños de negocio en Colombia.
Ofreces 3 verticales:
1. Bellia Flow: Embudos CRO y Agentes de Venta IA 24/7 en WhatsApp (Ejemplos: Landing Inositol, Joyería Ámbar).
2. Bellia Core: Procesamiento RAG de PDFs, manuales e inventarios masivos.
3. Bellia Guard: Motores Neuro-Simbólicos (DuckDB + SQL + IA) como en el caso de éxito 'Habla con los Contratos' (190.000+ contratos).

Responde siempre en español, de forma ejecutiva, cercana y empática. 
Intenta obtener: Nombre, Empresa/Sector y WhatsApp para agendar un diagnóstico técnico gratuito.
Cuando tengas estos datos, genera al final de tu mensaje el bloque:
[RESUMEN] Nombre: X | Empresa: Y | WhatsApp: Z | Necesidad: W [/RESUMEN]
"""

@app.get("/", response_class=HTMLResponse)
@limiter.limit("30/minute")
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/chat")
@limiter.limit("15/minute")
async def chat_endpoint(request: Request):
    data = await request.json()
    user_message = data.get("message", "")
    history = data.get("history", [])

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    for msg in history[-6:]: # Mantener contexto ligero
        messages.append({"role": msg["role"], "content": msg["content"]})
    messages.append({"role": "user", "content": user_message})

    try:
        completion = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            temperature=0.5,
            max_tokens=400
        )
        bot_response = completion.choices[0].message.content
    except Exception as e:
        # Fallback a modelo liviano si falla el principal
        try:
            completion = groq_client.chat.completions.create(
                model="llama3-8b-8192",
                messages=messages,
                temperature=0.5
            )
            bot_response = completion.choices[0].message.content
        except:
            bot_response = "En este momento estoy optimizando mis conexiones de datos. Déjame tu WhatsApp y te contactamos directamente."

    return JSONResponse({"response": bot_response})

@app.post("/procesar_lead")
@limiter.limit("5/minute")
async def procesar_lead(
    request: Request,
    nombre: str = Form(...),
    empresa: str = Form(""),
    whatsapp: str = Form(...),
    servicio: str = Form("General")
):
    conn = sqlite3.connect("bellia_leads.db")
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO leads (nombre, empresa, whatsapp, servicio) VALUES (?, ?, ?, ?)",
        (nombre, empresa, whatsapp, servicio)
    )
    conn.commit()
    conn.close()

    # Redirigir a WhatsApp con el mensaje estructurado
    msg = f"Hola Bellia! Soy {nombre} de {empresa}. Me interesa el servicio de {servicio} y solicitar mi diagnóstico gratuito."
    import urllib.parse
    encoded_msg = urllib.parse.quote(msg)
    ws_url = f"https://api.whatsapp.com/send?phone=573168331986&text={encoded_msg}"
    
    return JSONResponse({"status": "ok", "redirect_url": ws_url})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)