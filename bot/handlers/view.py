from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from bot.database.models import Expense, Income, TimeLog, Task, Note
from bot.database.db import SessionLocal
from bot.keyboards.keyboards import (
    get_view_menu_keyboard,
    get_main_keyboard,
)
from bot.utils.timezone import now

router = Router()

# Количество записей для просмотра
VIEW_LIMIT = 10
# Максимальная длина сообщения Telegram
MAX_MESSAGE_LENGTH = 4096


async def send_long_message(callback: CallbackQuery, text: str):
    """Отправка длинного сообщения с разбивкой на части"""
    if len(text) <= MAX_MESSAGE_LENGTH:
        try:
            await callback.message.edit_text(text)
        except Exception:
            await callback.message.answer(text)
        return

    # Разбиваем на части
    parts = []
    current_part = ""
    lines = text.split("\n")

    for line in lines:
        if len(current_part) + len(line) + 1 > MAX_MESSAGE_LENGTH:
            if current_part:
                parts.append(current_part)
            current_part = line
        else:
            current_part += "\n" + line if current_part else line

    if current_part:
        parts.append(current_part)

    # Отправляем первую часть через edit_text, остальные через answer
    if parts:
        try:
            await callback.message.edit_text(parts[0])
        except Exception:
            await callback.message.answer(parts[0])
        for part in parts[1:]:
            await callback.message.answer(part)


def format_expense(expense: Expense) -> str:
    """Форматирование расхода для отображения"""
    date_str = expense.date.strftime("%d.%m %H:%M")
    comment = f"\n  {expense.comment}" if expense.comment else ""
    return f"• {date_str} | {expense.category} | {expense.amount}сум{comment}"


def format_income(income: Income) -> str:
    """Форматирование дохода для отображения"""
    date_str = income.date.strftime("%d.%m %H:%M")
    comment = f"\n  {income.comment}" if income.comment else ""
    return f"• {date_str} | {income.category} | +{income.amount}сум{comment}"


def format_time_log(log: TimeLog) -> str:
    """Форматирование лога времени для отображения"""
    time_str = log.timestamp.strftime("%d.%m %H:%M")
    energy_str = f"+{log.energy}" if log.energy > 0 else str(log.energy)
    comment = f"\n  {log.comment}" if log.comment else ""
    return (
        f"• {time_str} | {log.activity_type} | {log.intention} | {energy_str}{comment}"
    )


def format_task(task: Task, show_complete_button: bool = False) -> str:
    """Форматирование задачи для отображения"""
    date_str = task.created_at.strftime("%d.%m %H:%M")
    device = f" | {task.device}" if task.device else ""
    status = "✅ ВЫПОЛНЕНО" if task.completed_at else f"[{task.status}]"
    return f"• {date_str} | {status} {task.task_type} | {task.title}{device}"


def format_note(note: Note) -> str:
    """Форматирование заметки для отображения"""
    date_str = note.timestamp.strftime("%d.%m %H:%M")
    # Обрезаем длинные заметки
    text = note.text[:200] + "..." if len(note.text) > 200 else note.text
    return f"• {date_str}\n  {text}"


@router.message(F.text == "👁 Просмотр")
async def view_start(message: Message):
    """Начало диалога просмотра данных"""
    await message.answer(
        "Выбери тип данных для просмотра:",
        reply_markup=get_view_menu_keyboard(),
    )


@router.callback_query(F.data == "view_expenses")
async def view_expenses(callback: CallbackQuery):
    """Просмотр расходов"""
    db = SessionLocal()
    try:
        expenses = (
            db.query(Expense).order_by(Expense.date.desc()).limit(VIEW_LIMIT).all()
        )

        if not expenses:
            try:
                await callback.message.edit_text("Нет записей о расходах.")
            except Exception:
                await callback.message.answer("Нет записей о расходах.")
            await callback.answer()
            return

        text = "💸 Последние расходы:\n\n"
        for expense in expenses:
            text += format_expense(expense) + "\n"

        # Добавляем общую сумму
        total = sum(e.amount for e in expenses)
        text += f"\nВсего: {total}сум"

        await send_long_message(callback, text)
        await callback.answer()
    finally:
        db.close()


@router.callback_query(F.data == "view_incomes")
async def view_incomes(callback: CallbackQuery):
    """Просмотр доходов"""
    db = SessionLocal()
    try:
        incomes = db.query(Income).order_by(Income.date.desc()).limit(VIEW_LIMIT).all()

        if not incomes:
            try:
                await callback.message.edit_text("Нет записей о доходах.")
            except Exception:
                await callback.message.answer("Нет записей о доходах.")
            await callback.answer()
            return

        text = "💰 Последние доходы:\n\n"
        for income in incomes:
            text += format_income(income) + "\n"

        # Добавляем общую сумму
        total = sum(i.amount for i in incomes)
        text += f"\nВсего: +{total}сум"

        await send_long_message(callback, text)
        await callback.answer()
    finally:
        db.close()


@router.callback_query(F.data == "view_time_logs")
async def view_time_logs(callback: CallbackQuery):
    """Просмотр логов времени"""
    db = SessionLocal()
    try:
        logs = (
            db.query(TimeLog).order_by(TimeLog.timestamp.desc()).limit(VIEW_LIMIT).all()
        )

        if not logs:
            try:
                await callback.message.edit_text("Нет записей логов времени.")
            except Exception:
                await callback.message.answer("Нет записей логов времени.")
            await callback.answer()
            return

        text = "⏱ Последние логи времени:\n\n"
        for log in logs:
            text += format_time_log(log) + "\n"

        await send_long_message(callback, text)
        await callback.answer()
    finally:
        db.close()


@router.callback_query(F.data == "view_tasks")
async def view_tasks(callback: CallbackQuery):
    """Просмотр задач"""
    db = SessionLocal()
    try:
        # Получаем активные задачи (не выполненные)
        active_tasks = (
            db.query(Task)
            .filter(Task.completed_at.is_(None))
            .order_by(Task.created_at.desc())
            .limit(VIEW_LIMIT)
            .all()
        )

        # Получаем выполненные задачи
        completed_tasks = (
            db.query(Task)
            .filter(Task.completed_at.isnot(None))
            .order_by(Task.completed_at.desc())
            .limit(5)
            .all()
        )

        if not active_tasks and not completed_tasks:
            try:
                await callback.message.edit_text("Нет записей задач.")
            except Exception:
                await callback.message.answer("Нет записей задач.")
            await callback.answer()
            return

        text = "🧠 Задачи:\n\n"

        # Группируем активные задачи по статусу
        current_tasks = [t for t in active_tasks if t.status == "СЕЙЧАС"]
        waiting_tasks = [t for t in active_tasks if t.status == "ЖДЁТ"]

        if current_tasks:
            text += "СЕЙЧАС:\n"
            for task in current_tasks:
                text += format_task(task) + "\n"
            text += "\n"

        if waiting_tasks:
            text += "ЖДЁТ:\n"
            for task in waiting_tasks:
                text += format_task(task) + "\n"
            text += "\n"

        if completed_tasks:
            text += "✅ ВЫПОЛНЕНО:\n"
            for task in completed_tasks:
                text += format_task(task) + "\n"

        # Создаем inline-кнопки для завершения активных задач
        from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

        inline_keyboard = []
        for task in active_tasks[:5]:  # Показываем кнопки для первых 5 активных задач
            inline_keyboard.append(
                [
                    InlineKeyboardButton(
                        text=f"✅ {task.title[:30]}...",
                        callback_data=f"complete_task_{task.id}",
                    )
                ]
            )

        keyboard = (
            InlineKeyboardMarkup(inline_keyboard=inline_keyboard)
            if inline_keyboard
            else None
        )

        if keyboard:
            try:
                await callback.message.edit_text(text, reply_markup=keyboard)
            except Exception:
                await callback.message.answer(text, reply_markup=keyboard)
        else:
            await send_long_message(callback, text)
        await callback.answer()
    finally:
        db.close()


@router.callback_query(F.data == "view_notes")
async def view_notes(callback: CallbackQuery):
    """Просмотр заметок"""
    db = SessionLocal()
    try:
        notes = db.query(Note).order_by(Note.timestamp.desc()).limit(VIEW_LIMIT).all()

        if not notes:
            try:
                await callback.message.edit_text("Нет записей заметок.")
            except Exception:
                await callback.message.answer("Нет записей заметок.")
            await callback.answer()
            return

        text = "📝 Последние заметки:\n\n"
        for note in notes:
            text += format_note(note) + "\n\n"

        # Создаем inline-кнопки для просмотра полного текста заметок
        from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

        inline_keyboard = []
        for note in notes:
            # Показываем кнопку только если заметка обрезана
            if len(note.text) > 200:
                note_preview = note.text[:30].replace("\n", " ")
                inline_keyboard.append(
                    [
                        InlineKeyboardButton(
                            text=f"📖 {note_preview}...",
                            callback_data=f"view_note_full_{note.id}",
                        )
                    ]
                )

        keyboard = (
            InlineKeyboardMarkup(inline_keyboard=inline_keyboard)
            if inline_keyboard
            else None
        )

        if keyboard:
            try:
                await callback.message.edit_text(text, reply_markup=keyboard)
            except Exception:
                await callback.message.answer(text, reply_markup=keyboard)
        else:
            await send_long_message(callback, text)
        await callback.answer()
    finally:
        db.close()


@router.callback_query(F.data.startswith("view_note_full_"))
async def view_note_full(callback: CallbackQuery):
    """Просмотр полного текста заметки"""
    try:
        note_id = int(callback.data.replace("view_note_full_", ""))
    except ValueError:
        await callback.answer("Ошибка: неверный ID заметки", show_alert=True)
        return

    db = SessionLocal()
    try:
        note = db.query(Note).filter(Note.id == note_id).first()
        if not note:
            await callback.answer("Заметка не найдена", show_alert=True)
            return

        date_str = note.timestamp.strftime("%d.%m.%Y %H:%M")
        text = f"📝 Заметка от {date_str}\n\n{note.text}"

        # Создаем кнопку "Назад" для возврата к списку
        from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="← Назад к списку", callback_data="view_notes"
                    )
                ]
            ]
        )

        await callback.message.edit_text(text, reply_markup=keyboard)
        await callback.answer()
    except Exception as e:
        await callback.answer(f"Ошибка: {str(e)}", show_alert=True)
    finally:
        db.close()


@router.callback_query(F.data.startswith("complete_task_"))
async def complete_task(callback: CallbackQuery):
    """Завершение задачи"""
    try:
        task_id = int(callback.data.replace("complete_task_", ""))
    except ValueError:
        await callback.answer("Ошибка: неверный ID задачи", show_alert=True)
        return

    db = SessionLocal()
    try:
        task = db.query(Task).filter(Task.id == task_id).first()
        if not task:
            await callback.answer("Задача не найдена", show_alert=True)
            return

        if task.completed_at:
            await callback.answer("Задача уже выполнена", show_alert=True)
            return

        # Отмечаем задачу как выполненную
        task.completed_at = now()
        db.commit()

        await callback.answer(f"✅ Задача '{task.title[:30]}...' выполнена!")
        await callback.message.edit_text(
            f"✅ Задача выполнена:\n{task.title}\n\nТип: {task.task_type}\nСтатус: {task.status}"
        )
    except Exception as e:
        db.rollback()
        await callback.answer(f"Ошибка: {str(e)}", show_alert=True)
    finally:
        db.close()
