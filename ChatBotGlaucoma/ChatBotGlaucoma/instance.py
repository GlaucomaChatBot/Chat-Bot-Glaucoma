import asyncio
from pathlib import Path
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, Router
from aiogram.client.bot import DefaultBotProperties
from aiogram.enums import ParseMode
import os
import sqlite3
from database.db_requests import GlaucomaDB

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
if not TELEGRAM_TOKEN:
    raise ValueError("Не указан TELEGRAM_TOKEN в .env файле")

bot = Bot(
    token=TELEGRAM_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)

dp = Dispatcher()
main_router = Router()

def init_database() -> GlaucomaDB:
    db_path = Path(__file__).parent / "database" / "glaucoma.db"
    db = GlaucomaDB(str(db_path))
    
    try:
        db.conn.execute("SELECT 1")
        print(f"База данных успешно подключена, путь к ней: {db_path}")
        return db
    except sqlite3.Error as e:
        raise ConnectionError(f"Ошибка подключения к БД: {e}")

try:
    db = init_database()
except Exception as e:
    print(f"Ошибка инициализации БД: {e}")
    raise

async def on_startup():
    from handlers import notifications  # Импорт здесь, чтобы избежать циклического импорта
    asyncio.create_task(notifications.send_medication_reminders())
    print("Система уведомлений запущена")

user_states = {}