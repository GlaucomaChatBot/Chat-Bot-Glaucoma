from telegram.ext import ApplicationBuilder, CommandHandler # для формирования бота в принципе
from dotenv import load_dotenv # для загрузки токена
import os

# импорт обработчиков
from handlers.start_handler import start # обработка старта
from handlers.faq_handler import question_handler # обработка кнопки вопросы
from handlers.medicine_handler import add_medicine # обработка кнопки добавления лекарства

# Загрузка .env
load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    # Обработчики команд
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("faq", question_handler))
    app.add_handler(CommandHandler("add", add_medicine))

    print("Бот запущен!") # просто для проверки, уберем потом
    app.run_polling()

if __name__ == "__main__":
    main()

