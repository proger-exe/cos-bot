from aiogram.fsm.state import State, StatesGroup


class FinanceFlow(StatesGroup):
    """Состояния для диалога добавления расхода"""

    waiting_for_category = State()
    waiting_for_amount = State()
    waiting_for_comment = State()


class TimeLogFlow(StatesGroup):
    """Состояния для диалога лога времени"""

    waiting_for_activity = State()
    waiting_for_intention = State()
    waiting_for_energy = State()
    waiting_for_comment = State()


class TaskFlow(StatesGroup):
    """Состояния для диалога добавления задачи"""

    waiting_for_type = State()
    waiting_for_status = State()
    waiting_for_title = State()
    waiting_for_device = State()


class NoteFlow(StatesGroup):
    """Состояния для диалога добавления заметки"""

    waiting_for_text = State()


class IncomeFlow(StatesGroup):
    """Состояния для диалога добавления дохода"""

    waiting_for_category = State()
    waiting_for_amount = State()
    waiting_for_comment = State()
