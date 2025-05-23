import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

class Config:
    BASE_DIR = Path(__file__).parent.parent
    DATA_DIR = Path("C:/Users/Lenovo/Desktop/voice_assistant/data")
    
    # PostgreSQL settings
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", "5433")
    DB_NAME = os.getenv("DB_NAME", "web_data_demo")
    DB_USER = os.getenv("DB_USER", "postgres")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")
    DB_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
  
    # NLP settings
    STOP_WORDS = ["и", "в", "на", "о", "с", "по", "для"]
    
    # Voice settings
    VOICE_ENABLED = True
    VOICE_RATE = 150
    VOICE_VOLUME = 0.9
    
    # Security settings
    MAX_QUERY_LENGTH = 500
    ALLOWED_CHARS = set("абвгдеёжзийклмнопрстуфхцчшщъыьэюяАБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯabcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 -,.:;!?()")