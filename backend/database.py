from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import text

# Используем асинхронный драйвер aiosqlite
# Файл базы данных будет создан в корне проекта
SQLITE_FILE_NAME = "ai_database.db"
DATABASE_URL = f"sqlite+aiosqlite:///{SQLITE_FILE_NAME}"

engine = create_async_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
Base = declarative_base()

async def get_db():
    async with SessionLocal() as session:
        yield session

# Эта функция будет использоваться для создания таблиц
async def create_db_and_tables():
    async with engine.begin() as conn:
        # Для SQLite foreign key constraints могут требовать явного включения
        await conn.execute(text("PRAGMA foreign_keys = ON;"))
        # Создаем все таблицы, определенные в Base.metadata (в models.py)
        await conn.run_sync(Base.metadata.create_all)