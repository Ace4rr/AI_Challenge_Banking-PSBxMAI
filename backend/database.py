# backend/database.py

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import text 
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
    try:
        async with engine.begin() as conn:
            # Создаем все таблицы, определенные в Base.metadata (в models.py)
            await conn.run_sync(Base.metadata.create_all)
        print("Database and tables created successfully!") 
    except Exception as e:
        # !!! ВЫВОДИМ ПОДРОБНУЮ ОШИБКУ !!!
        print(f"!!! КРИТИЧЕСКАЯ ОШИБКА БД: Не удалось создать таблицы. Проверьте PostgreSQL. Ошибка: {e}")
        # Чтобы uvicorn прекратил запуск и показал ошибку
        raise e