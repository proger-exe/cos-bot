from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from bot.database.models import Expense
from bot.database.db import SessionLocal
from bot.keyboards.keyboards import get_finance_categories_keyboard, get_main_keyboard
from bot.states.states import FinanceFlow
from bot.utils.timezone import now

router = Router()


@router.message(F.text == "💸 Расход")
async def finance_start(message: Message, state: FSMContext):
    """Начало диалога добавления расхода"""
    await message.answer(
        "Выбери категорию расхода:", reply_markup=get_finance_categories_keyboard()
    )
    await state.set_state(FinanceFlow.waiting_for_category)


@router.callback_query(
    F.data.startswith("finance_category_"), FinanceFlow.waiting_for_category
)
async def finance_category_selected(callback: CallbackQuery, state: FSMContext):
    """Обработка выбора категории"""
    category = callback.data.replace("finance_category_", "")
    await state.update_data(category=category)
    await callback.message.edit_text(f"Категория: {category}\n\nВведи сумму (число):")
    await state.set_state(FinanceFlow.waiting_for_amount)
    await callback.answer()


@router.message(FinanceFlow.waiting_for_amount)
async def finance_amount_input(message: Message, state: FSMContext):
    """Обработка ввода суммы"""
    try:
        amount = float(message.text.replace(",", "."))
        if amount <= 0:
            await message.answer(
                "Сумма должна быть положительным числом. Попробуй ещё раз:"
            )
            return

        await state.update_data(amount=amount)
        await message.answer("Введи комментарий (или отправь /skip чтобы пропустить):")
        await state.set_state(FinanceFlow.waiting_for_comment)
    except ValueError:
        await message.answer("Неверный формат. Введи число (например: 1500 или 99.50):")


@router.message(FinanceFlow.waiting_for_comment)
async def finance_comment_input(message: Message, state: FSMContext):
    """Обработка ввода комментария или завершение"""
    comment = None
    if message.text and message.text != "/skip":
        comment = message.text

    data = await state.get_data()
    category = data.get("category")
    amount = data.get("amount")

    # Сохранение в БД
    db = SessionLocal()
    try:
        expense = Expense(date=now(), category=category, amount=amount, comment=comment)
        db.add(expense)
        db.commit()

        response = f"✅ Расход записан:\nКатегория: {category}\nСумма: {amount}"
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
