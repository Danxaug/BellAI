from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from app.core.config import get_settings
from app.core.lifespan import lifespan
from app.core.logging import configure_logging
from app.core.middleware import RequestIDMiddleware, SecurityHeadersMiddleware
from app.routers import pages, chat, leads, health

settings = get_settings()
configure_logging(debug=settings.APP_DEBUG)

limiter = Limiter(key_func=get_remote_address)
app = FastAPI(
    title=settings.APP_NAME,
    description="Bellia — AI & Tech Agency. Ecosistema de automatización cognitiva.",
    version="1.0.0",
    lifespan=lifespan,
    # En producción, deshabilitamos docs:
    docs_url=None if settings.APP_ENV == "production" else "/docs",
    redoc_url=None if settings.APP_ENV == "production" else "/redoc",
    openapi_url=None if settings.APP_ENV == "production" else "/openapi.json",
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Middleware (orden importa: seguridad envolvente + request ID)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RequestIDMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# Static y routers
app.mount("/static", StaticFiles(directory="static"), name="static")
app.include_router(pages.router, tags=["pages"])
app.include_router(chat.router, tags=["chat"])
app.include_router(leads.router, tags=["leads"])
app.include_router(health.router, tags=["health"])