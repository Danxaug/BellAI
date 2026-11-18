from fastapi import APIRouter, Request, HTTPException
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.core.logging import get_logger
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.ai import generate_reply

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)
logger = get_logger("chat")


@router.post("/chat", response_model=ChatResponse)
@limiter.limit("15/minute")
async def chat_endpoint(request: Request, payload: ChatRequest):
    request_id = getattr(request.state, "request_id", "n/a")
    logger.info(
        "chat_request",
        request_id=request_id,
        history_len=len(payload.history),
        msg_len=len(payload.message),
    )
    try:
        response = await generate_reply(
            payload.message,
            [m.model_dump() for m in payload.history],
        )
    except Exception as e:
        logger.error("chat_failed", request_id=request_id, error=str(e))
        raise HTTPException(status_code=500, detail="Servicio temporalmente no disponible")

    return ChatResponse(response=response)