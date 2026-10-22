#!/usr/bin/env python3
"""
Скрипт миграции базы данных COS

Добавляет:
- Таблицу incomes (доходы)
- Поле completed_at в таблицу tasks

Запуск: python migrate.py
"""

import sys
import os
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.exc import OperationalError

# Добавляем путь к модулям бота
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from bot.config import DATABASE_PATH
from bot.database.models import Base, Income, Task


def check_table_exists(engine, table_name: str) -> bool:
    """Проверка существования таблицы"""
    inspector = inspect(engine)
    return table_name in inspector.get_table_names()


def check_column_exists(engine, table_name: str, column_name: str) -> bool:
    """Проверка существования колонки в таблице"""
    inspector = inspect(engine)
    columns = [col["name"] for col in inspector.get_columns(table_name)]
    return column_name in columns


def migrate():
    """Выполнение миграции"""
    print(f"Подключение к базе данных: {DATABASE_PATH}")

    if not os.path.exists(DATABASE_PATH):
        print(f"⚠️  База данных {DATABASE_PATH} не найдена.")
        print("База будет создана при первом запуске бота.")
        return

    engine = create_engine(f"sqlite:///{DATABASE_PATH}", echo=False)

    print("\n🔍 Проверка структуры базы данных...\n")

    # 1. Проверка и создание таблицы incomes
    if not check_table_exists(engine, "incomes"):
        print("📊 Создание таблицы incomes...")
        Income.__table__.create(engine)
        print("✅ Таблица incomes создана")
    else:
        print("✅ Таблица incomes уже существует")

    # 2. Проверка и добавление поля completed_at в таблицу tasks
    if check_table_exists(engine, "tasks"):
        if not check_column_exists(engine, "tasks", "completed_at"):
            print("📊 Добавление поля completed_at в таблицу tasks...")
            with engine.connect() as conn:
                conn.execute(text("ALTER TABLE tasks ADD COLUMN completed_at DATETIME"))
                conn.commit()
            print("✅ Поле completed_at добавлено в таблицу tasks")
        else:
            print("✅ Поле completed_at уже существует в таблице tasks")
    else:
        print("⚠️  Таблица tasks не найдена (будет создана при первом запуске)")

    print("\n✨ Миграция завершена успешно!")


if __name__ == "__main__":
    try:
        migrate()
    except Exception as e:
        print(f"\n❌ Ошибка при выполнении миграции: {e}")
        sys.exit(1)
