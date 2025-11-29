# backend/database.py

import os
from dotenv import load_dotenv # <-- НОВЫЙ ИМПОРТ
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, func, Text
from typing import AsyncGenerator
from fastapi import Depends

# Загружаем переменные окружения, чтобы получить URL базы данных
load_dotenv() 

# =========================================================
# === КОНФИГУРАЦИЯ БАЗЫ ДАННЫХ (PostgreSQL) ===
# =========================================================

# Используйте переменную окружения DATABASE_URL
# Формат: postgresql+asyncpg://<пользователь>:<пароль>@<хост>:<порт>/<имя_бд>
SQLALCHEMY_DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql+asyncpg://postgres:password@localhost:5432/my_database"
)

# Инициализация Engine (удален connect_args, специфичный для SQLite)
# 'echo=True' оставил для вывода SQL-запросов в консоль
engine = create_async_engine(SQLALCHEMY_DATABASE_URL, echo=True)
Base = declarative_base()
AsyncSessionLocal = async_sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=AsyncSession)


# =========================================================
# === МОДЕЛЬ ДАННЫХ (с новыми полями) ===
# =========================================================

class Message(Base):
    """Модель для хранения анализируемых сообщений."""
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    input_text = Column(Text, nullable=False)

    # Старые поля
    category = Column(String)
    official_reply = Column(Text)
    parameters = Column(Text)

    # НОВЫЕ ПОЛЯ
    reply_style = Column(String)
    time_to_reply = Column(String)
    summary = Column(Text)
    infrastructure_sphere = Column(String)
    risks_and_fixes = Column(Text)

    created_at = Column(DateTime, default=func.now())


# =========================================================
# === ФУНКЦИИ, ТРЕБУЕМЫЕ В main.py ===
# =========================================================

async def create_db_and_tables():
    """Создает таблицы в базе данных."""
    async with engine.begin() as conn:
        # ВНИМАНИЕ: ВРЕМЕННО РАСКОММЕНТИРУЙТЕ ЭТУ СТРОКУ, 
        # ЧТОБЫ УДАЛИТЬ СТАРУЮ ТАБЛИЦУ С НЕПРАВИЛЬНОЙ СХЕМОЙ!
        await conn.run_sync(Base.metadata.drop_all) 
        
        # Создание новых таблиц (с правильной схемой)
        await conn.run_sync(Base.metadata.create_all)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency-функция для получения асинхронной сессии БД."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()