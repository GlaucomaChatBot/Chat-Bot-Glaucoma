# кнопки с функциями (изменить на инлайны)

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

async def main_menu_keyboard():
    keyboard = [
        [KeyboardButton(text="Добавить лекарство для отслеживания и напоминаний")],
        [KeyboardButton(text="Ответить на интересующие вопросы")]
    ]

    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)