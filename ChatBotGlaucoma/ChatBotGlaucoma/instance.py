# ����-����������� ����, ��������
# �������� ������ ��������� �� ����� db = DataBaseClass()

from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, Router
from aiogram.client.bot import DefaultBotProperties
from aiogram.enums import ParseMode

import os

# �������� ����
load_dotenv()
bot = Bot(os.getenv("TELEGRAM_TOKEN"),default=DefaultBotProperties(parse_mode=ParseMode.HTML))

# �������� ����������
dp = Dispatcher()

# �������� �������� �������
main_router = Router()

# ��� ��