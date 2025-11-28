# backend/database.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import text # Оставляем для PRAGMA, но в Postgres не нужно
import os

# Используйте переменную окружения или значение по умолчанию для PostgreSQL
# Ваша строка подключения: postgresql+asyncpg://postgres:6585@localhost/hackdb
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:6585@localhost/hackdb")

engine = create_async_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
Base = declarative_base()

async def get_db():
    async with SessionLocal() as session:
        yield session

# Эта функция будет использоваться для создания таблиц
async def create_db_and_tables():
    async with engine.begin() as conn:
        # Убираем строку "PRAGMA foreign_keys = ON;" - она нужна только для SQLite
        #await conn.execute(text("PRAGMA foreign_keys = ON;")) 

        # Создаем все таблицы, определенные в Base.metadata (в models.py)
        await conn.run_sync(Base.metadata.create_all)