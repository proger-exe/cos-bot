import asyncio
import random
import logging
from datetime import timedelta
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiogram import Bot
from bot.database.models import Expense, TimeLog, Task, Note
from bot.database.db import SessionLocal
from bot.config import REMINDER_MESSAGES, REMINDER_INTERVALS
from bot.utils.timezone import now

logger = logging.getLogger(__name__)


class ReminderService:
    """Сервис напоминаний о необходимости фиксации данных"""

    def __init__(self, bot: Bot):
        self.bot = bot
        self.scheduler = AsyncIOScheduler()
        self.user_id = None  # Будет установлен при первом сообщении

    def set_user_id(self, user_id: int):
        """Установить ID пользователя для отправки напоминаний"""
        self.user_id = user_id

    def has_recent_activity(self, hours: int = 6) -> bool:
        """Проверить наличие активности за последние N часов"""
        if not self.user_id:
            return True  # Если пользователь не установлен, не напоминаем

        cutoff_time = now() - timedelta(hours=hours)
        db = SessionLocal()
        try:
            # Проверяем наличие записей за последние N часов
            has_expense = (
                db.query(Expense).filter(Expense.date >= cutoff_time).first()
                is not None
            )
            has_time_log = (
                db.query(TimeLog).filter(TimeLog.timestamp >= cutoff_time).first()
                is not None
            )
            has_task = (
                db.query(Task).filter(Task.created_at >= cutoff_time).first()
                is not None
            )
            has_note = (
                db.query(Note).filter(Note.timestamp >= cutoff_time).first() is not None
            )

            return has_expense or has_time_log or has_task or has_note
        finally:
            db.close()

    async def send_reminder(self):
        """Отправить напоминание пользователю"""
        if not self.user_id:
            return

        # Проверяем активность за последние 6 часов
        if not self.has_recent_activity(hours=6):
            message = random.choice(REMINDER_MESSAGES)
            try:
                await self.bot.send_message(self.user_id, message)
            except Exception as e:
                logger.error(f"Ошибка отправки напоминания: {e}")

    def start(self):
        """Запустить сервис напоминаний"""
        # Напоминания 3-5 раз в день (каждые 4-6 часов)
        # Используем случайный интервал из списка для разнообразия
        interval = random.choice(REMINDER_INTERVALS)

        # Добавляем задачу с интервалом
        self.scheduler.add_job(
            self.send_reminder,
            "interval",
            hours=interval,
            id="reminder_job",
            replace_existing=True,
        )

        self.scheduler.start()
        logger.info(f"Reminder service started with {interval}h interval")

    def stop(self):
        """Остановить сервис напоминаний"""
        self.scheduler.shutdown()
