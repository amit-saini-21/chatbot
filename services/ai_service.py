import os
import json
import re
from typing import Dict

import google.generativeai as genai
from dotenv import load_dotenv

from models import role_model as role_db
from services.image_generation_service import generate_image_base64
from utils.image_prompt_builder import build_default_appearance, build_image_prompt
from utils.intent_detection import IntentResult, detect_image_intent
from utils.prompt_builder import build_prompt
from utils.safety_filter import evaluate_image_safety, safe_fallback_message

load_dotenv()

_GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
if _GEMINI_API_KEY:
    genai.configure(api_key=_GEMINI_API_KEY)

_GEMINI_MODEL = genai.GenerativeModel("gemini-3-flash-preview") if _GEMINI_API_KEY else None
_ENABLE_SEMANTIC_INTENT = os.getenv("ENABLE_SEMANTIC_INTENT", "false").strip().lower() == "true"
_ENABLE_SEMANTIC_SAFETY = os.getenv("ENABLE_SEMANTIC_SAFETY", "false").strip().lower() == "true"


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


def _extract_json_object(text: str):
    if not text:
        return None

    candidate = text.strip()
    fenced_match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", candidate, flags=re.DOTALL)
    if fenced_match:
        candidate = fenced_match.group(1).strip()

    if not candidate.startswith("{"):
        start = candidate.find("{")
        end = candidate.rfind("}")
        if start == -1 or end == -1 or end <= start:
            return None
        candidate = candidate[start : end + 1]

    try:
        return json.loads(candidate)
    except Exception:
        return None


def _semantic_intent_detection(user_message: str):
    if not _GEMINI_MODEL:
        return None

    prompt = (
        "Classify the user request for an AI chat backend. "
        "Input can be in any language. "
        "Return STRICT JSON only with keys: "
        "is_image_request (boolean), intent_type (text|image|diagram), "
        "wants_diagram (boolean), confidence (0..1). "
        f"User message: {user_message}"
    )

    try:
        response = _GEMINI_MODEL.generate_content(prompt)
    except Exception:
        return None

    parsed = _extract_json_object(getattr(response, "text", ""))
    if not parsed:
        return None

    intent_type = str(parsed.get("intent_type", "text")).lower().strip()
    if intent_type not in {"text", "image", "diagram"}:
        intent_type = "text"

    return IntentResult(
        is_image_request=bool(parsed.get("is_image_request", False)),
        intent_type=intent_type,
        confidence=float(parsed.get("confidence", 0.0) or 0.0),
        wants_diagram=bool(parsed.get("wants_diagram", False) or intent_type == "diagram"),
    )


def _semantic_safety_check(user_message: str):
    if not _GEMINI_MODEL:
        return None

    prompt = (
        "Safety classify this potential image-generation request in any language. "
        "Return STRICT JSON only with keys: "
        "is_safe (boolean), category (none|sexual_explicit|minor_related|graphic_violence|self_harm|hate_or_extremism). "
        "Unsafe includes sexual/NSFW, minors, graphic harm, self-harm, hate/extremism. "
        f"User message: {user_message}"
    )

    try:
        response = _GEMINI_MODEL.generate_content(prompt)
    except Exception:
        return None

    parsed = _extract_json_object(getattr(response, "text", ""))
    if not parsed:
        return None

    return {
        "is_safe": bool(parsed.get("is_safe", True)),
        "category": str(parsed.get("category", "none")).strip().lower(),
    }


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

    if _ENABLE_SEMANTIC_INTENT and not intent.is_image_request and intent.confidence < 0.55:
        semantic_intent = _semantic_intent_detection(user_message)
        if semantic_intent and semantic_intent.is_image_request:
            intent = semantic_intent

    if not intent.is_image_request:
        text_response = _generate_text_response(user_message, role, messages, memory)
        if not text_response:
            text_response = "I could not process that request right now. Please try again."
        return {"type": "text", "data": text_response}

    if not _can_generate_image(role_type, intent.intent_type):
        return {"type": "text", "data": _permission_denied_message(role_type)}

    safety = evaluate_image_safety(user_message)
    if _ENABLE_SEMANTIC_SAFETY and safety.is_safe:
        semantic_safety = _semantic_safety_check(user_message)
        if semantic_safety and not semantic_safety.get("is_safe", True):
            return {"type": "text", "data": safe_fallback_message()}

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