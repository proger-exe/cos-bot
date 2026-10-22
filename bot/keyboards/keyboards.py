from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)


# Постоянная Reply клавиатура
def get_main_keyboard() -> ReplyKeyboardMarkup:
    """Главная клавиатура с основными действиями"""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="💸 Расход"), KeyboardButton(text="💰 Доход")],
            [KeyboardButton(text="⏱ Лог времени"), KeyboardButton(text="🧠 Задача")],
            [
                KeyboardButton(text="📝 Заметка"),
                KeyboardButton(text="📊 Экспорт"),
                KeyboardButton(text="👁 Просмотр"),
            ],
        ],
        resize_keyboard=True,
        persistent=True,
    )
    return keyboard


# Inline клавиатуры для финансов
def get_finance_categories_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура выбора категории расхода"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Обязательное", callback_data="finance_category_Обязательное"
                ),
                InlineKeyboardButton(
                    text="Проекты", callback_data="finance_category_Проекты"
                ),
            ],
            [
                InlineKeyboardButton(text="Еда", callback_data="finance_category_Еда"),
                InlineKeyboardButton(
                    text="Инфра", callback_data="finance_category_Инфра"
                ),
            ],
            [
                InlineKeyboardButton(
                    text="Импульс", callback_data="finance_category_Импульс"
                ),
                InlineKeyboardButton(
                    text="Транспорт", callback_data="finance_category_Транспорт"
                ),
            ],
            [
                InlineKeyboardButton(
                    text="Здоровье", callback_data="finance_category_Здоровье"
                ),
                InlineKeyboardButton(
                    text="Развлечения", callback_data="finance_category_Развлечения"
                ),
            ],
            [
                InlineKeyboardButton(
                    text="Одежда", callback_data="finance_category_Одежда"
                ),
                InlineKeyboardButton(
                    text="Подарки", callback_data="finance_category_Подарки"
                ),
            ],
        ]
    )
    return keyboard


def get_income_categories_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура выбора категории дохода"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Зарплата", callback_data="income_category_Зарплата"
                ),
                InlineKeyboardButton(
                    text="Фриланс", callback_data="income_category_Фриланс"
                ),
            ],
            [
                InlineKeyboardButton(
                    text="Проекты", callback_data="income_category_Проекты"
                ),
                InlineKeyboardButton(
                    text="Инвестиции", callback_data="income_category_Инвестиции"
                ),
            ],
            [
                InlineKeyboardButton(
                    text="Подарки", callback_data="income_category_Подарки"
                ),
                InlineKeyboardButton(
                    text="Прочее", callback_data="income_category_Прочее"
                ),
            ],
        ]
    )
    return keyboard


# Inline клавиатуры для логов времени
def get_activity_types_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура выбора типа активности"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Работа", callback_data="activity_Работа"),
                InlineKeyboardButton(text="Учеба", callback_data="activity_Учеба"),
            ],
            [
                InlineKeyboardButton(text="Отдых", callback_data="activity_Отдых"),
                InlineKeyboardButton(text="Сон", callback_data="activity_Сон"),
            ],
            [
                InlineKeyboardButton(text="Рутина", callback_data="activity_Рутина"),
                InlineKeyboardButton(text="Арх", callback_data="activity_Арх"),
            ],
        ]
    )
    return keyboard


def get_intention_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура выбора намерения"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="План", callback_data="intention_План"),
                InlineKeyboardButton(text="Вынужд", callback_data="intention_Вынужд"),
                InlineKeyboardButton(text="Утекло", callback_data="intention_Утекло"),
            ]
        ]
    )
    return keyboard


def get_energy_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура выбора энергии"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="+1", callback_data="energy_1"),
                InlineKeyboardButton(text="0", callback_data="energy_0"),
                InlineKeyboardButton(text="-1", callback_data="energy_-1"),
            ]
        ]
    )
    return keyboard


# Inline клавиатуры для задач
def get_task_type_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура выбора типа задачи"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Работа", callback_data="task_type_Работа"),
                InlineKeyboardButton(text="Учеба", callback_data="task_type_Учеба"),
            ],
            [
                InlineKeyboardButton(text="Отдых", callback_data="task_type_Отдых"),
                InlineKeyboardButton(text="Сон", callback_data="task_type_Сон"),
            ],
            [
                InlineKeyboardButton(text="Рутина", callback_data="task_type_Рутина"),
                InlineKeyboardButton(text="Арх", callback_data="task_type_Арх"),
            ],
        ]
    )
    return keyboard


def get_task_status_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура выбора статуса задачи"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="СЕЙЧАС", callback_data="task_status_СЕЙЧАС"),
                InlineKeyboardButton(text="ЖДЁТ", callback_data="task_status_ЖДЁТ"),
            ]
        ]
    )
    return keyboard


def get_device_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура выбора устройства"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="A→B", callback_data="device_A→B"),
                InlineKeyboardButton(text="B→A", callback_data="device_B→A"),
                InlineKeyboardButton(text="—", callback_data="device_—"),
            ]
        ]
    )
    return keyboard


# Inline клавиатуры для экспорта
def get_export_period_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура выбора периода экспорта"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="День", callback_data="export_period_day"),
                InlineKeyboardButton(text="Неделя", callback_data="export_period_week"),
                InlineKeyboardButton(text="Месяц", callback_data="export_period_month"),
            ]
        ]
    )
    return keyboard


# Inline клавиатуры для просмотра
def get_view_menu_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура выбора типа данных для просмотра"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="💸 Расходы", callback_data="view_expenses"),
                InlineKeyboardButton(text="💰 Доходы", callback_data="view_incomes"),
            ],
            [
                InlineKeyboardButton(
                    text="⏱ Логи времени", callback_data="view_time_logs"
                ),
                InlineKeyboardButton(text="🧠 Задачи", callback_data="view_tasks"),
            ],
            [
                InlineKeyboardButton(text="📝 Заметки", callback_data="view_notes"),
            ],
        ]
    )
    return keyboard
