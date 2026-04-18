import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "this_is_a_secret_key_for_my_flask_based_chatbot_application")
    DATABASE_URI = os.getenv("DATABASE_URI", "")
    MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "ai_chat_db")
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
    GEMINI_API_KEY_2 = os.getenv("GEMINI_API_KEY_2", "").strip()
    GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3-flash-preview")
    SHORT_TERM_MEMORY_LIMIT = int(os.getenv("SHORT_TERM_MEMORY_LIMIT", "5"))