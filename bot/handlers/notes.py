from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from bot.database.models import Note
from bot.database.db import SessionLocal
from bot.keyboards.keyboards import get_main_keyboard
from bot.states.states import NoteFlow
from bot.utils.timezone import now

router = Router()


@router.message(F.text == "📝 Заметка")
async def note_start(message: Message, state: FSMContext):
    """Начало диалога добавления заметки"""
    await message.answer("Введи текст заметки:")
    await state.set_state(NoteFlow.waiting_for_text)


@router.message(NoteFlow.waiting_for_text)
async def note_text_input(message: Message, state: FSMContext):
    """Обработка ввода текста заметки"""
    text = message.text.strip()
    if not text:
        await message.answer("Текст заметки не может быть пустым. Введи текст:")
        return

    # Сохранение в БД
    db = SessionLocal()
    try:
        note = Note(text=text, timestamp=now())
        db.add(note)
        db.commit()

        await message.answer("✅ Заметка записана.", reply_markup=get_main_keyboard())
    except Exception as e:
        db.rollback()
        await message.answer(
            f"Ошибка при сохранении: {str(e)}", reply_markup=get_main_keyboard()
        )
    finally:
        db.close()

    await state.clear()
