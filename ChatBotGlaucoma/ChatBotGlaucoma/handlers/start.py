from aiogram.types import Message
from aiogram import F

from instance import main_router  # импорт главного роутера
from keyboards import reply       # импорт клавы

# подвязка хендлера к главному роутеру

@main_router.message(F.text == "/start") # слово запускающее бота

async def func(message: Message):
    await message.answer(text="тут приветственное сообщение",reply_markup=await reply.main_menu_keyboard())