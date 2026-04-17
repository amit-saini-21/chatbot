import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "your_default_secret_key")
    DATABASE_URI = os.getenv("DATABASE_URI", "sqlite:///chatbot.db")    
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "your_default_gemini_api_key")