from mangum import Mangum
from app.main import app

# Handler para Vercel (serverless)
handler = Mangum(app, lifespan="off")
