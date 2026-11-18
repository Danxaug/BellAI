# Bellia — Activo Tecnológico

Plataforma de IA y automatización cognitiva.

## Stack
FastAPI · SQLAlchemy 2 async · Postgres/SQLite · Redis · Groq · Tailwind (build local)

## Setup local
```bash
cp .env.example .env       # rellena GROQ_API_KEY y SECRET_KEY
python -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
npm install && npm run build:css
uvicorn app.main:app --reload