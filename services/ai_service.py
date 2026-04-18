import os
import google.generativeai as genai
from dotenv import load_dotenv
from utils.prompt_builder import build_prompt

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


def get_ai_response(user_message, role, messages, memory=None):

    text_response = _generate_text_response(user_message, role, messages, memory)
    if not text_response:
        text_response = "I could not process that request right now. Please try again."
    return {"type": "text", "data": text_response}
