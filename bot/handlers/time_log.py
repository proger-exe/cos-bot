from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from bot.database.models import TimeLog
from bot.database.db import SessionLocal
from bot.keyboards.keyboards import (
    get_activity_types_keyboard,
    get_intention_keyboard,
    get_energy_keyboard,
    get_main_keyboard,
)
from bot.states.states import TimeLogFlow
from bot.utils.timezone import now

router = Router()


@router.message(F.text == "⏱ Лог времени")
async def time_log_start(message: Message, state: FSMContext):
    """Начало диалога лога времени"""
    await message.answer(
        "Выбери тип активности:", reply_markup=get_activity_types_keyboard()
    )
    await state.set_state(TimeLogFlow.waiting_for_activity)


@router.callback_query(F.data.startswith("activity_"), TimeLogFlow.waiting_for_activity)
async def activity_selected(callback: CallbackQuery, state: FSMContext):
    """Обработка выбора типа активности"""
    activity_type = callback.data.replace("activity_", "")
    await state.update_data(activity_type=activity_type)
    await callback.message.edit_text(
        f"Активность: {activity_type}\n\nВыбери намерение:",
        reply_markup=get_intention_keyboard(),
    )
    await state.set_state(TimeLogFlow.waiting_for_intention)
    await callback.answer()


@router.callback_query(
    F.data.startswith("intention_"), TimeLogFlow.waiting_for_intention
)
async def intention_selected(callback: CallbackQuery, state: FSMContext):
    """Обработка выбора намерения"""
    intention = callback.data.replace("intention_", "")
    await state.update_data(intention=intention)
    await callback.message.edit_text(
        f"Намерение: {intention}\n\nВыбери энергию:", reply_markup=get_energy_keyboard()
    )
    await state.set_state(TimeLogFlow.waiting_for_energy)
    await callback.answer()


@router.callback_query(F.data.startswith("energy_"), TimeLogFlow.waiting_for_energy)
async def energy_selected(callback: CallbackQuery, state: FSMContext):
    """Обработка выбора энергии"""
    energy_str = callback.data.replace("energy_", "")
    energy = int(energy_str)
    await state.update_data(energy=energy)
    await callback.message.edit_text(
        f"Энергия: {energy_str}\n\nВведи комментарий (или отправь /skip чтобы пропустить):"
    )
    await state.set_state(TimeLogFlow.waiting_for_comment)
    await callback.answer()


@router.message(TimeLogFlow.waiting_for_comment)
async def time_log_comment_input(message: Message, state: FSMContext):
    """Обработка ввода комментария или завершение"""
    comment = None
    if message.text and message.text != "/skip":
        comment = message.text

    data = await state.get_data()
    activity_type = data.get("activity_type")
    intention = data.get("intention")
    energy = data.get("energy")

    # Сохранение в БД
    db = SessionLocal()
    try:
        time_log = TimeLog(
            timestamp=now(),
            activity_type=activity_type,
            intention=intention,
            energy=energy,
            comment=comment,
        )
        db.add(time_log)
        db.commit()

        response = f"✅ Лог записан:\nАктивность: {activity_type}\nНамерение: {intention}\nЭнергия: {energy}"
        if comment:
            response += f"\nКомментарий: {comment}"

        await message.answer(response, reply_markup=get_main_keyboard())
    except Exception as e:
        db.rollback()
        await message.answer(
            f"Ошибка при сохранении: {str(e)}", reply_markup=get_main_keyboard()
        )
    finally:
        db.close()

    await state.clear()
