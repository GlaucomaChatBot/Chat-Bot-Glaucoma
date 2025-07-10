import asyncio
from instance import bot, dp, main_router, on_startup
from handlers import start, notifications

async def main():
    # Регистрируем обработчик запуска
    dp.startup.register(on_startup)
    
    # Подключаем все роутеры
    dp.include_router(main_router)  # Основные команды (/start и текстовые сообщения)
    dp.include_router(notifications.router)  # Обработчики кнопок подтверждения
    
    # Запускаем фоновую задачу для уведомлений
    asyncio.create_task(notifications.send_medication_reminders())
    
    print("Бот запущен! Система уведомлений активна.")
    try:
        await dp.start_polling(bot, timeout=10, skip_updates=True)
    except Exception as e:
        print(f"Ошибка при polling: {e}")

if __name__ == "__main__":
    asyncio.run(main())