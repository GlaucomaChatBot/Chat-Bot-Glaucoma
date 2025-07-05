from telegram.ext import ApplicationBuilder, CommandHandler # ��� ������������ ���� � ��������
from dotenv import load_dotenv # ��� �������� ������
import os

# ������ ������������
from handlers.start_handler import start # ��������� ������
from handlers.faq_handler import question_handler # ��������� ������ �������
from handlers.medicine_handler import add_medicine # ��������� ������ ���������� ���������

# �������� .env
load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    # ����������� ������
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("faq", question_handler))
    app.add_handler(CommandHandler("add", add_medicine))

    print("��� �������!") # ������ ��� ��������, ������ �����
    app.run_polling()

if __name__ == "__main__":
    main()

