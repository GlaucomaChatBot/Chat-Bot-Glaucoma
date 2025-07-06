# ФАЙЛ-КОНСТРУКТОР БОТА, ЗАВЕРШЕН
# ОСТАЛОСЬ ТОЛЬКО ПРИВЯЗАТЬ БД ЧЕРЕЗ db = DataBaseClass()

from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, Router
from aiogram.client.bot import DefaultBotProperties
from aiogram.enums import ParseMode

import os

# создание бота
load_dotenv()
bot = Bot(os.getenv("TELEGRAM_TOKEN"),default=DefaultBotProperties(parse_mode=ParseMode.HTML))

# создание диспетчера
dp = Dispatcher()

# создание главного роутера
main_router = Router()

# тут бд