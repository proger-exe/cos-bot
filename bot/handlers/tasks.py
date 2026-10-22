from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from bot.database.models import Task
from bot.database.db import SessionLocal
from bot.keyboards.keyboards import (
    get_task_type_keyboard,
    get_task_status_keyboard,
    get_device_keyboard,
    get_main_keyboard,
)
from bot.states.states import TaskFlow
from bot.utils.timezone import now

router = Router()

MAX_CURRENT_TASKS = 5


@router.message(F.text == "🧠 Задача")
async def task_start(message: Message, state: FSMContext):
    """Начало диалога добавления задачи"""
    await message.answer("Выбери тип задачи:", reply_markup=get_task_type_keyboard())
    await state.set_state(TaskFlow.waiting_for_type)


@router.callback_query(F.data.startswith("task_type_"), TaskFlow.waiting_for_type)
async def task_type_selected(callback: CallbackQuery, state: FSMContext):
    """Обработка выбора типа задачи"""
    task_type = callback.data.replace("task_type_", "")
    await state.update_data(task_type=task_type)
    await callback.message.edit_text(
        f"Тип задачи: {task_type}\n\nВыбери статус:",
        reply_markup=get_task_status_keyboard(),
    )
    await state.set_state(TaskFlow.waiting_for_status)
    await callback.answer()


@router.callback_query(F.data.startswith("task_status_"), TaskFlow.waiting_for_status)
async def task_status_selected(callback: CallbackQuery, state: FSMContext):
    """Обработка выбора статуса задачи"""
    status = callback.data.replace("task_status_", "")
    data = await state.get_data()

    # Проверка лимита для статуса "СЕЙЧАС" (только невыполненные задачи)
    if status == "СЕЙЧАС":
        db = SessionLocal()
        try:
            current_count = (
                db.query(Task)
                .filter(Task.status == "СЕЙЧАС", Task.completed_at.is_(None))
                .count()
            )
            if current_count >= MAX_CURRENT_TASKS:
                await callback.answer(
                    f"Лимит задач в статусе 'СЕЙЧАС' ({MAX_CURRENT_TASKS}) достигнут. "
                    "Заверши или перемести существующие задачи.",
                    show_alert=True,
                )
                return
        finally:
            db.close()

    await state.update_data(status=status)
    await callback.message.edit_text(f"Статус: {status}\n\nВведи название задачи:")
    await state.set_state(TaskFlow.waiting_for_title)
    await callback.answer()


@router.message(TaskFlow.waiting_for_title)
async def task_title_input(message: Message, state: FSMContext):
    """Обработка ввода названия задачи"""
    title = message.text.strip()
    if not title:
        await message.answer("Название не может быть пустым. Введи название задачи:")
        return

    await state.update_data(title=title)
    await message.answer(
        "Выбери устройство (или отправь /skip чтобы пропустить):",
        reply_markup=get_device_keyboard(),
    )
    await state.set_state(TaskFlow.waiting_for_device)


@router.callback_query(F.data.startswith("device_"), TaskFlow.waiting_for_device)
async def device_selected(callback: CallbackQuery, state: FSMContext):
    """Обработка выбора устройства или завершение"""
    device = callback.data.replace("device_", "")
    if device == "—":
        device = None

    data = await state.get_data()
    title = data.get("title")
    task_type = data.get("task_type")
    status = data.get("status")

    # Сохранение в БД
    db = SessionLocal()
    try:
        task = Task(
            title=title,
            task_type=task_type,
            status=status,
            device=device,
            created_at=now(),
        )
        db.add(task)
        db.commit()

        response = f"✅ Задача записана:\nТип: {task_type}\nСтатус: {status}\nНазвание: {title}"
        if device:
            response += f"\nУстройство: {device}"

        await callback.message.edit_text(response)
        await callback.message.answer(
            "Задача добавлена.", reply_markup=get_main_keyboard()
        )
    except Exception as e:
        db.rollback()
        await callback.message.answer(
            f"Ошибка при сохранении: {str(e)}", reply_markup=get_main_keyboard()
        )
    finally:
        db.close()

    await state.clear()
    await callback.answer()


@router.message(TaskFlow.waiting_for_device)
async def task_device_skip(message: Message, state: FSMContext):
    """Обработка пропуска выбора устройства"""
    if message.text == "/skip":
        data = await state.get_data()
        title = data.get("title")
        task_type = data.get("task_type")
        status = data.get("status")

        # Сохранение в БД
        db = SessionLocal()
        try:
            task = Task(
                title=title,
                task_type=task_type,
                status=status,
                device=None,
                created_at=now(),
            )
            db.add(task)
            db.commit()

            response = f"✅ Задача записана:\nТип: {task_type}\nСтатус: {status}\nНазвание: {title}"
            await message.answer(response, reply_markup=get_main_keyboard())
        except Exception as e:
            db.rollback()
            await message.answer(
                f"Ошибка при сохранении: {str(e)}", reply_markup=get_main_keyboard()
            )
        finally:
            db.close()

        await state.clear()
    else:
        await message.answer(
            "Используй кнопки для выбора устройства или отправь /skip:"
        )
