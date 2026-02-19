import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))
    PSYCHOLOGIST_USERNAME = os.getenv("PSYCHOLOGIST_USERNAME", "@psychologist")
    CHANNEL_ID = os.getenv("CHANNEL_ID", "")
    CHANNEL_INVITE_LINK = os.getenv("CHANNEL_INVITE_LINK", "")
    DB_PATH = os.getenv("DB_PATH", "users.db")
    
    # Валидация
    if not BOT_TOKEN:
        raise ValueError("❌ BOT_TOKEN не установлен в .env файле")
    if not ADMIN_ID:
        raise ValueError("❌ ADMIN_ID не установлен в .env файле")
    if not PSYCHOLOGIST_USERNAME.startswith("@"):
        raise ValueError("❌ PSYCHOLOGIST_USERNAME должен начинаться с @")
    if not CHANNEL_ID:
        raise ValueError("❌ CHANNEL_ID не установлен в .env файле")