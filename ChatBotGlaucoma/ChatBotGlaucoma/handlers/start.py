from telegram import Update
from telegram.ext import ContextTypes
from keyboards.reply import main_menu_keyboard

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = (
        "Привет! Я бот, который поможет тебе не забыть принять лекарства и ответит на важные вопросы.\n\n"
        "Выбери действие ниже:"
    )
    await update.message.reply_text(welcome_text, reply_markup=main_menu_keyboard())
