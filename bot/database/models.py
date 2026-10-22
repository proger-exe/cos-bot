from sqlalchemy import Column, Integer, String, Float, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from bot.utils.timezone import now

Base = declarative_base()


class Expense(Base):
    """Модель расходов"""

    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime, default=now, nullable=False)
    category = Column(String(50), nullable=False)
    amount = Column(Float, nullable=False)
    comment = Column(Text, nullable=True)


class Income(Base):
    """Модель доходов"""

    __tablename__ = "incomes"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime, default=now, nullable=False)
    category = Column(String(50), nullable=False)
    amount = Column(Float, nullable=False)
    comment = Column(Text, nullable=True)


class TimeLog(Base):
    """Модель логов времени и энергии"""

    __tablename__ = "time_logs"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=now, nullable=False)
    activity_type = Column(String(20), nullable=False)
    intention = Column(String(20), nullable=False)
    energy = Column(Integer, nullable=False)  # -1, 0, or 1
    comment = Column(Text, nullable=True)


class Task(Base):
    """Модель задач"""

    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(500), nullable=False)
    task_type = Column(String(20), nullable=False)
    status = Column(String(20), nullable=False)
    device = Column(String(10), nullable=True)
    created_at = Column(DateTime, default=now, nullable=False)
    completed_at = Column(DateTime, nullable=True)


class Note(Base):
    """Модель заметок"""

    __tablename__ = "notes"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=now, nullable=False)
