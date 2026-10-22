import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
DATABASE_PATH = os.getenv("DATABASE_PATH", "cos.db")

# Reminder settings
REMINDER_MESSAGES = [
    "Нет записей. Фиксируй.",
    "Ты живёшь без логов.",
    "Записи отсутствуют.",
    "Фиксируй реальность.",
    "Нет данных за сегодня.",
]

# Reminder schedule: 3-5 times per day (every 4-6 hours)
REMINDER_INTERVALS = [4, 5, 6]  # hours
