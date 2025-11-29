from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:6585@localhost/hackdb")

engine = create_async_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
Base = declarative_base()

async def get_db():
    async with SessionLocal() as session:
        yield session


async def create_db_and_tables():
    try:
        async with engine.begin() as conn:

            await conn.run_sync(Base.metadata.create_all)
        print("Database and tables created successfully!") 
    except Exception as e:

        print(f"!!! КРИТИЧЕСКАЯ ОШИБКА БД: Не удалось создать таблицы. Проверьте PostgreSQL. Ошибка: {e}")
        raise e