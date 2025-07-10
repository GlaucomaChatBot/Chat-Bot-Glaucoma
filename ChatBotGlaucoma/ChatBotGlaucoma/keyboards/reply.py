from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

async def role_selection_keyboard() -> ReplyKeyboardMarkup:
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Я врач"), KeyboardButton(text="Я пациент")]
        ],
        resize_keyboard=True
    )
    return keyboard

async def main_menu_keyboard() -> ReplyKeyboardMarkup:
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Мои лекарства")],
            [KeyboardButton(text="Добавить лекарство")],
            [KeyboardButton(text="История приёмов")],
            [KeyboardButton(text="Выбрать своего врача")]
        ],
        resize_keyboard=True
    )
    return keyboard

async def doctor_menu_keyboard() -> ReplyKeyboardMarkup:
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Мои пациенты")],
            [KeyboardButton(text="Просмотреть пропуски")],
        ],
        resize_keyboard=True
    )
    return keyboard

async def cancel_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="Отмена")]],
        resize_keyboard=True,
        one_time_keyboard=True
    )