import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from bot.config import BOT_TOKEN
from bot.database.db import init_db
from bot.handlers import common, finance, income, time_log, tasks, notes, export, view
from bot.services.reminder import ReminderService


# Настройка логирования
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def main():
    """Главная функция запуска бота"""
    if not BOT_TOKEN:
        logger.error("BOT_TOKEN не установлен! Создай файл .env с BOT_TOKEN=...")
        return

    # Инициализация БД
    init_db()
    logger.info("База данных инициализирована")

    # Инициализация бота и диспетчера
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())

    # Инициализация сервиса напоминаний
    reminder_service = ReminderService(bot)

    # Регистрация роутеров
    dp.include_router(common.router)
    dp.include_router(finance.router)
    dp.include_router(income.router)
    dp.include_router(time_log.router)
    dp.include_router(tasks.router)
    dp.include_router(notes.router)
    dp.include_router(export.router)
    dp.include_router(view.router)
    # Запуск бота
    logger.info("Бот запущен")
    try:
        await dp.start_polling(
            bot,
            allowed_updates=dp.resolve_used_update_types(),
            reminder_service=reminder_service,
        )
    finally:
        reminder_service.stop()
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
