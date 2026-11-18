from functools import lru_cache
from pathlib import Path
from groq import AsyncGroq
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
import httpx
from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger("ai")
settings = get_settings()
PROMPT_PATH = Path(__file__).parent.parent / "prompts" / "v1_system.md"

@lru_cache
def get_system_prompt() -> str:
    if PROMPT_PATH.exists():
        return PROMPT_PATH.read_text(encoding="utf-8")
    return "Eres Bellia AI, asesor de tecnología."

@lru_cache
def get_groq_client() -> AsyncGroq:
    return AsyncGroq(api_key=settings.GROQ_API_KEY, timeout=settings.GROQ_TIMEOUT)

@retry(stop=stop_after_attempt(2), wait=wait_exponential(multiplier=0.5, min=0.5, max=3), retry=retry_if_exception_type((httpx.TimeoutException, httpx.HTTPError)), reraise=False)
async def _call_groq(model: str, messages: list[dict]) -> str:
    client = get_groq_client()
    completion = await client.chat.completions.create(
        model=model, messages=messages, temperature=0.5, max_tokens=400,
    )
    return completion.choices[0].message.content

async def generate_reply(user_message: str, history: list[dict]) -> str:
    messages = [{"role": "system", "content": get_system_prompt()}]
    messages.extend(history)
    messages.append({"role": "user", "content": user_message})
    try:
        return await _call_groq(settings.GROQ_MODEL_PRIMARY, messages)
    except Exception as e:
        logger.warning("groq_primary_failed", error=str(e))
        try:
            return await _call_groq(settings.GROQ_MODEL_FALLBACK, messages)
        except Exception as e2:
            logger.error("groq_all_failed", error=str(e2))
            return "En este momento estoy optimizando mis conexiones. Déjame tu WhatsApp y te contactamos."