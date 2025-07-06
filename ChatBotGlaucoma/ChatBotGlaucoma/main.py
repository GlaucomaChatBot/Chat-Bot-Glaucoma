import asyncio

from instance import bot, dp, main_router

# импорты файлов с хендлерами
import handlers.start # тут будут обработчики через запятую по мере разработки

async def main() -> None:

    # рег главного роутера
    dp.include_router(main_router)

    print("Bot is run!") # сообщение что бот запустился

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

