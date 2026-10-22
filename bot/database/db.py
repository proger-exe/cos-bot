from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from bot.config import DATABASE_PATH
from bot.database.models import Base

engine = create_engine(f"sqlite:///{DATABASE_PATH}", echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """Инициализация базы данных - создание всех таблиц"""
    Base.metadata.create_all(bind=engine)


def get_db() -> Session:
    """Получение сессии БД"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
