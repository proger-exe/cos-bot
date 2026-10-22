from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from bot.database.models import Income
from bot.database.db import SessionLocal
from bot.keyboards.keyboards import get_income_categories_keyboard, get_main_keyboard
from bot.states.states import IncomeFlow
from bot.utils.timezone import now

router = Router()


@router.message(F.text == "💰 Доход")
async def income_start(message: Message, state: FSMContext):
    """Начало диалога добавления дохода"""
    await message.answer(
        "Выбери категорию дохода:", reply_markup=get_income_categories_keyboard()
    )
    await state.set_state(IncomeFlow.waiting_for_category)


@router.callback_query(
    F.data.startswith("income_category_"), IncomeFlow.waiting_for_category
)
async def income_category_selected(callback: CallbackQuery, state: FSMContext):
    """Обработка выбора категории"""
    category = callback.data.replace("income_category_", "")
    await state.update_data(category=category)
    await callback.message.edit_text(f"Категория: {category}\n\nВведи сумму (число):")
    await state.set_state(IncomeFlow.waiting_for_amount)
    await callback.answer()


@router.message(IncomeFlow.waiting_for_amount)
async def income_amount_input(message: Message, state: FSMContext):
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
        await state.set_state(IncomeFlow.waiting_for_comment)
    except ValueError:
        await message.answer("Неверный формат. Введи число (например: 1500 или 99.50):")


@router.message(IncomeFlow.waiting_for_comment)
async def income_comment_input(message: Message, state: FSMContext):
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
        income = Income(date=now(), category=category, amount=amount, comment=comment)
        db.add(income)
        db.commit()

        response = f"✅ Доход записан:\nКатегория: {category}\nСумма: {amount}"
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
