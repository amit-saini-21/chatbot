import os
from typing import Dict

import google.generativeai as genai
from dotenv import load_dotenv

from models import role_model as role_db
from services.image_generation_service import generate_image_base64
from utils.image_prompt_builder import build_default_appearance, build_image_prompt
from utils.intent_detection import detect_image_intent
from utils.prompt_builder import build_prompt
from utils.safety_filter import evaluate_image_safety, safe_fallback_message

load_dotenv()

_GEMINI_API_KEY = os.getenv("GEMINI_API_KEY_2", "").strip()
if _GEMINI_API_KEY:
    genai.configure(api_key=_GEMINI_API_KEY)

_GEMINI_MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-3-flash-preview")
_GEMINI_MODEL = genai.GenerativeModel(_GEMINI_MODEL_NAME) if _GEMINI_API_KEY else None


def _generate_text_response(user_message, role, messages, memory=None):
    if not _GEMINI_MODEL:
        return None

    prompt = build_prompt(role, messages, user_message, memory)

    try:
        response = _GEMINI_MODEL.generate_content(prompt)
        return response.text
    except Exception as exc:
        print(f"Gemini Error: {exc}")
        return None


def _can_generate_image(role_type: str, intent_type: str) -> bool:
    normalized_role = (role_type or "assistant").lower()

    if normalized_role in {"girlfriend", "boyfriend", "friend"}:
        return True

    if normalized_role == "teacher":
        return intent_type == "diagram"

    # Assistant is intentionally restricted from image generation.
    return False


def _permission_denied_message(role_type: str) -> str:
    normalized_role = (role_type or "assistant").lower()
    if normalized_role == "teacher":
        return "Teacher mode can generate educational diagrams only."
    if normalized_role == "assistant":
        return "Assistant mode does not support image generation in this chat."
    return "This role is not allowed to generate images."


def _ensure_role_appearance(role: Dict) -> str:
    appearance = role_db.get_role_appearance(role)
    if appearance:
        return appearance

    generated_appearance = build_default_appearance(role)
    role_id = role.get("_id")
    if role_id:
        role_db.set_role_appearance(role_id, generated_appearance)
    return generated_appearance


def get_ai_response(user_message, role, messages, memory=None):
    role_type = (role or {}).get("role_type", "assistant")
    intent = detect_image_intent(user_message)

    if not intent.is_image_request:
        text_response = _generate_text_response(user_message, role, messages, memory)
        if not text_response:
            text_response = "I could not process that request right now. Please try again."
        return {"type": "text", "data": text_response}

    if not _can_generate_image(role_type, intent.intent_type):
        return {"type": "text", "data": _permission_denied_message(role_type)}

    safety = evaluate_image_safety(user_message)
    if not safety.is_safe:
        return {"type": "text", "data": safe_fallback_message()}

    appearance = _ensure_role_appearance(role)
    image_prompt = build_image_prompt(
        user_message=user_message,
        role=role,
        appearance=appearance,
        intent_type=intent.intent_type,
    )

    image_b64, image_error = generate_image_base64(image_prompt)
    if image_error or not image_b64:
        return {
            "type": "text",
            "data": "Image generation is currently unavailable. Please try again later.",
            "meta": {"image_error": image_error},
        }

    return {
        "type": "image",
        "data": {
            "base64": image_b64,
            "mime_type": "image/png",
        },
    }