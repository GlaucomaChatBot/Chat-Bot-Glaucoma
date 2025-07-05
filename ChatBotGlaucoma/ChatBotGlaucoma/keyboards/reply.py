from telegram import ReplyKeyboardMarkup, KeyboardButton

def main_menu_keyboard():

    keyboard = [
        [KeyboardButton("Добавить лекарство для отслеживания и напоминаний")],
        [KeyboardButton("Ответить на интересующие вопросы")]
    ]

    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)