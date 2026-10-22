from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, BufferedInputFile
from bot.keyboards.keyboards import get_export_period_keyboard, get_main_keyboard
from bot.services.export_service import (
    export_expenses_csv,
    export_incomes_csv,
    export_finance_summary_csv,
    export_time_logs_csv,
    export_tasks_csv,
)
from bot.utils.timezone import now

router = Router()


@router.message(F.text == "📊 Экспорт")
async def export_start(message: Message):
    """Начало диалога экспорта"""
    await message.answer(
        "Выбери период экспорта:", reply_markup=get_export_period_keyboard()
    )


@router.callback_query(F.data.startswith("export_period_"))
async def export_period_selected(callback: CallbackQuery):
    """Обработка выбора периода и генерация CSV файлов"""
    period = callback.data.replace("export_period_", "")

    period_names = {"day": "День", "week": "Неделя", "month": "Месяц"}
    period_name = period_names.get(period, period)

    await callback.message.edit_text(f"Генерирую экспорт за {period_name}...")

    try:
        # Экспорт сводки по финансам (доходы и расходы)
        finance_summary_csv = export_finance_summary_csv(period)
        finance_summary_file = BufferedInputFile(
            finance_summary_csv.getvalue().encode("utf-8-sig"),
            filename=f"finance_summary_{period}_{now().strftime('%Y%m%d')}.csv",
        )
        await callback.message.answer_document(
            finance_summary_file, caption=f"Сводка по финансам за {period_name}"
        )

        # Экспорт расходов
        expenses_csv = export_expenses_csv(period)
        expenses_file = BufferedInputFile(
            expenses_csv.getvalue().encode("utf-8-sig"),
            filename=f"expenses_{period}_{now().strftime('%Y%m%d')}.csv",
        )
        await callback.message.answer_document(
            expenses_file, caption=f"Расходы за {period_name}"
        )

        # Экспорт доходов
        incomes_csv = export_incomes_csv(period)
        incomes_file = BufferedInputFile(
            incomes_csv.getvalue().encode("utf-8-sig"),
            filename=f"incomes_{period}_{now().strftime('%Y%m%d')}.csv",
        )
        await callback.message.answer_document(
            incomes_file, caption=f"Доходы за {period_name}"
        )

        # Экспорт логов времени
        time_logs_csv = export_time_logs_csv(period)
        time_logs_file = BufferedInputFile(
            time_logs_csv.getvalue().encode("utf-8-sig"),
            filename=f"time_logs_{period}_{now().strftime('%Y%m%d')}.csv",
        )
        await callback.message.answer_document(
            time_logs_file, caption=f"Логи времени за {period_name}"
        )

        # Экспорт задач
        tasks_csv = export_tasks_csv(period)
        tasks_file = BufferedInputFile(
            tasks_csv.getvalue().encode("utf-8-sig"),
            filename=f"tasks_{period}_{now().strftime('%Y%m%d')}.csv",
        )
        await callback.message.answer_document(
            tasks_file,
            caption=f"Задачи за {period_name}",
            reply_markup=get_main_keyboard(),
        )

        await callback.answer("Экспорт завершён")
    except Exception as e:
        await callback.message.answer(
            f"Ошибка при экспорте: {str(e)}", reply_markup=get_main_keyboard()
        )
        await callback.answer("Ошибка экспорта", show_alert=True)
