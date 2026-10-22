import csv
import io
from datetime import datetime, timedelta
from typing import Tuple
from bot.database.models import Expense, Income, TimeLog, Task
from bot.database.db import SessionLocal
from bot.utils.timezone import now


def get_date_range(period: str) -> Tuple[datetime, datetime]:
    """Получить диапазон дат для периода"""
    current_time = now()
    if period == "day":
        start = current_time.replace(hour=0, minute=0, second=0, microsecond=0)
        end = current_time
    elif period == "week":
        start = (current_time - timedelta(days=current_time.weekday())).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        end = current_time
    elif period == "month":
        start = current_time.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        end = current_time
    else:
        # Для неопределенного периода используем широкий диапазон
        tz = current_time.tzinfo
        start = datetime(2000, 1, 1, tzinfo=tz)
        end = datetime(2100, 12, 31, 23, 59, 59, tzinfo=tz)

    return start, end


def export_expenses_csv(period: str) -> io.StringIO:
    """Экспорт расходов в CSV с итогами"""
    start_date, end_date = get_date_range(period)

    db = SessionLocal()
    try:
        expenses = (
            db.query(Expense)
            .filter(Expense.date >= start_date, Expense.date <= end_date)
            .order_by(Expense.date)
            .all()
        )

        output = io.StringIO()
        writer = csv.writer(output)

        # Заголовки
        writer.writerow(["Дата", "Категория", "Сумма", "Комментарий"])

        # Данные
        category_totals = {}
        total = 0.0

        for expense in expenses:
            writer.writerow(
                [
                    expense.date.strftime("%Y-%m-%d %H:%M:%S"),
                    expense.category,
                    expense.amount,
                    expense.comment or "",
                ]
            )
            # Подсчитываем итоги
            total += expense.amount
            category_totals[expense.category] = (
                category_totals.get(expense.category, 0) + expense.amount
            )

        # Пустая строка перед итогами
        writer.writerow([])

        # Итоги по категориям
        if category_totals:
            writer.writerow(["ИТОГО (Расходы по категориям)"])
            for category in sorted(category_totals.keys()):
                writer.writerow(["", category, category_totals[category], ""])

        # Общий итог
        writer.writerow([])
        writer.writerow(["ИТОГО (Расходы)", "", total, ""])

        output.seek(0)
        return output
    finally:
        db.close()


def export_incomes_csv(period: str) -> io.StringIO:
    """Экспорт доходов в CSV с итогами"""
    start_date, end_date = get_date_range(period)

    db = SessionLocal()
    try:
        incomes = (
            db.query(Income)
            .filter(Income.date >= start_date, Income.date <= end_date)
            .order_by(Income.date)
            .all()
        )

        output = io.StringIO()
        writer = csv.writer(output)

        # Заголовки
        writer.writerow(["Дата", "Категория", "Сумма", "Комментарий"])

        # Данные
        category_totals = {}
        total = 0.0

        for income in incomes:
            writer.writerow(
                [
                    income.date.strftime("%Y-%m-%d %H:%M:%S"),
                    income.category,
                    income.amount,
                    income.comment or "",
                ]
            )
            # Подсчитываем итоги
            total += income.amount
            category_totals[income.category] = (
                category_totals.get(income.category, 0) + income.amount
            )

        # Пустая строка перед итогами
        writer.writerow([])

        # Итоги по категориям
        if category_totals:
            writer.writerow(["ИТОГО (Доходы по категориям)"])
            for category in sorted(category_totals.keys()):
                writer.writerow(["", category, category_totals[category], ""])

        # Общий итог
        writer.writerow([])
        writer.writerow(["ИТОГО (Доходы)", "", total, ""])

        output.seek(0)
        return output
    finally:
        db.close()


def export_finance_summary_csv(period: str) -> io.StringIO:
    """Экспорт сводки по финансам (доходы и расходы)"""
    start_date, end_date = get_date_range(period)

    db = SessionLocal()
    try:
        expenses = (
            db.query(Expense)
            .filter(Expense.date >= start_date, Expense.date <= end_date)
            .order_by(Expense.date)
            .all()
        )

        incomes = (
            db.query(Income)
            .filter(Income.date >= start_date, Income.date <= end_date)
            .order_by(Income.date)
            .all()
        )

        output = io.StringIO()
        writer = csv.writer(output)

        # РАСХОДЫ
        writer.writerow(["РАСХОДЫ"])
        writer.writerow(["Дата", "Категория", "Сумма", "Комментарий"])

        expense_category_totals = {}
        expense_total = 0.0

        for expense in expenses:
            writer.writerow(
                [
                    expense.date.strftime("%Y-%m-%d %H:%M:%S"),
                    expense.category,
                    expense.amount,
                    expense.comment or "",
                ]
            )
            expense_total += expense.amount
            expense_category_totals[expense.category] = (
                expense_category_totals.get(expense.category, 0) + expense.amount
            )

        writer.writerow([])

        # Итоги расходов по категориям
        if expense_category_totals:
            writer.writerow(["ИТОГО (Расходы по категориям)"])
            for category in sorted(expense_category_totals.keys()):
                writer.writerow(["", category, expense_category_totals[category], ""])

        # Общий итог расходов
        writer.writerow([])
        writer.writerow(["ИТОГО (Расходы)", "", expense_total, ""])

        writer.writerow([])
        writer.writerow([])

        # ДОХОДЫ
        writer.writerow(["ДОХОДЫ"])
        writer.writerow(["Дата", "Категория", "Сумма", "Комментарий"])

        income_category_totals = {}
        income_total = 0.0

        for income in incomes:
            writer.writerow(
                [
                    income.date.strftime("%Y-%m-%d %H:%M:%S"),
                    income.category,
                    income.amount,
                    income.comment or "",
                ]
            )
            income_total += income.amount
            income_category_totals[income.category] = (
                income_category_totals.get(income.category, 0) + income.amount
            )

        writer.writerow([])

        # Итоги доходов по категориям
        if income_category_totals:
            writer.writerow(["ИТОГО (Доходы по категориям)"])
            for category in sorted(income_category_totals.keys()):
                writer.writerow(["", category, income_category_totals[category], ""])

        # Общий итог доходов
        writer.writerow([])
        writer.writerow(["ИТОГО (Доходы)", "", income_total, ""])

        writer.writerow([])
        writer.writerow([])

        # ОБЩИЙ ИТОГ
        balance = income_total - expense_total
        writer.writerow(["ИТОГО (Общее)", "", balance, ""])

        output.seek(0)
        return output
    finally:
        db.close()


def export_time_logs_csv(period: str) -> io.StringIO:
    """Экспорт логов времени в CSV"""
    start_date, end_date = get_date_range(period)

    db = SessionLocal()
    try:
        logs = (
            db.query(TimeLog)
            .filter(TimeLog.timestamp >= start_date, TimeLog.timestamp <= end_date)
            .order_by(TimeLog.timestamp)
            .all()
        )

        output = io.StringIO()
        writer = csv.writer(output)

        # Заголовки
        writer.writerow(["Время", "Активность", "Намерение", "Энергия", "Комментарий"])

        # Данные
        for log in logs:
            writer.writerow(
                [
                    log.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                    log.activity_type,
                    log.intention,
                    log.energy,
                    log.comment or "",
                ]
            )

        output.seek(0)
        return output
    finally:
        db.close()


def export_tasks_csv(period: str) -> io.StringIO:
    """Экспорт задач в CSV"""
    start_date, end_date = get_date_range(period)

    db = SessionLocal()
    try:
        tasks = (
            db.query(Task)
            .filter(Task.created_at >= start_date, Task.created_at <= end_date)
            .order_by(Task.created_at)
            .all()
        )

        output = io.StringIO()
        writer = csv.writer(output)

        # Заголовки
        writer.writerow(
            ["Создано", "Тип", "Статус", "Название", "Устройство", "Выполнено"]
        )

        # Данные
        for task in tasks:
            completed_str = (
                task.completed_at.strftime("%Y-%m-%d %H:%M:%S")
                if task.completed_at
                else ""
            )
            status = "✅ ВЫПОЛНЕНО" if task.completed_at else task.status
            writer.writerow(
                [
                    task.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                    task.task_type,
                    status,
                    task.title,
                    task.device or "",
                    completed_str,
                ]
            )

        output.seek(0)
        return output
    finally:
        db.close()
