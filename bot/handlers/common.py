from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from bot.keyboards.keyboards import get_main_keyboard
from bot.services.reminder import ReminderService, logger

router = Router()


@router.message(Command("start"))
async def cmd_start(message: Message, reminder_service: ReminderService):
    if reminder_service.user_id is None and message.from_user:
        reminder_service.set_user_id(message.from_user.id)
        reminder_service.start()
        logger.info(f"Reminder service started for user {message.from_user.id}")

    """Обработчик команды /start"""
    await message.answer(
        "Добро пожаловать в COS (Cognitive Offload System).\n\n"
        "Используй клавиатуру для быстрого ввода данных.",
        reply_markup=get_main_keyboard(),
    )


@router.message(Command("help"))
async def cmd_help(message: Message):
    """Обработчик команды /help"""
    help_text = """
COS - Cognitive Offload System

Основные функции:
💸 Расход - учёт расходов по категориям
⏱ Лог времени - фиксация активности и энергии
🧠 Задача - управление задачами
📝 Заметка - быстрая запись мыслей
📊 Экспорт - выгрузка данных в CSV

Принцип: быстрый ввод (≤20 сек), анализ вне Telegram.
"""
    await message.answer(help_text, reply_markup=get_main_keyboard())
