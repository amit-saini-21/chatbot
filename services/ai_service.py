import logging
import os

import google.generativeai as genai
from dotenv import load_dotenv

from utils.prompt_builder import build_prompt

load_dotenv()

logger = logging.getLogger(__name__)

_GEMINI_API_KEYS = []
for env_name in ("GEMINI_API_KEY", "GEMINI_API_KEY_2"):
    value = os.getenv(env_name, "").strip()
    if value and value not in _GEMINI_API_KEYS:
        _GEMINI_API_KEYS.append(value)

_GEMINI_MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-3-flash-preview")
_FALLBACK_MESSAGE = "I could not process that request right now. Please try again."


def _generate_text_response(user_message, role, messages, memory=None):
    prompt = build_prompt(role, messages, user_message, memory)
    last_error = None

    for attempt, api_key in enumerate(_GEMINI_API_KEYS, start=1):
        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel(_GEMINI_MODEL_NAME)
            response = model.generate_content(prompt)
            text = getattr(response, "text", "") or ""
            if text.strip():
                return text.strip(), attempt
        except Exception as exc:
            last_error = exc
            logger.warning("Gemini request failed on key %s: %s", attempt, exc)

    if last_error:
        logger.error("All Gemini API keys failed", exc_info=last_error)
    return None, None


def get_ai_response(user_message, role, messages, memory=None):
    text_response, provider_attempt = _generate_text_response(user_message, role, messages, memory)
    if not text_response:
        return {
            "type": "text",
            "data": _FALLBACK_MESSAGE,
            "provider": "fallback",
        }

    return {
        "type": "text",
        "data": text_response,
        "provider": f"gemini-{provider_attempt}",
    }
