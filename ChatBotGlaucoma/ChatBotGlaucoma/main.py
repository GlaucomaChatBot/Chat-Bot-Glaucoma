from telegram.ext import ApplicationBuilder, CommandHandler # для формирования бота в принципе
from dotenv import load_dotenv # для загрузки токена
import os

# импорт обработчиков
from handlers.start import start # обработка старта
# from handlers.question import question # обработка кнопки вопросы (еще не реализовано, потом сделаю)
# from handlers.medicine import add # обработка кнопки добавления лекарства (еще не реализовано, потом сделаю)

# Загрузка .env
load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    # Обработчики команд
    app.add_handler(CommandHandler("start", start))
    # app.add_handler(CommandHandler("question", question))
    # app.add_handler(CommandHandler("add", add_medicine))

    print("Бот запущен!") # просто для проверки, уберем потом

    app.run_polling() # ← Ожидает завершения (ctrl+C)

if __name__ == "__main__":
    main()

