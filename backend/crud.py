# backend/crud.py

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
# Убедитесь, что Message импортирован правильно из database.py
from .database import Message 


# --- 1. Функция создания сообщения (со всеми 8 новыми полями) ---
async def create_message(
    db: AsyncSession, 
    text: str, 
    category: str, 
    official_reply: str, 
    parameters: str,
    reply_style: str, 
    time_to_reply: str, 
    summary: str, 
    infrastructure_sphere: str, 
    risks_and_fixes: str,
):
    """Создает и сохраняет новое сообщение в базе данных."""
    db_message = Message(
        input_text=text,
        category=category,
        official_reply=official_reply,
        parameters=parameters,
        
        # Новые поля
        reply_style=reply_style,
        time_to_reply=time_to_reply,
        summary=summary,
        infrastructure_sphere=infrastructure_sphere,
        risks_and_fixes=risks_and_fixes,
    )
    
    db.add(db_message)
    await db.commit()
    await db.refresh(db_message)
    return db_message


# --- 2. Функция получения всех сообщений (ОТСУТСТВОВАЛА) ---
async def get_messages(db: AsyncSession):
    """
    Возвращает список всех сообщений из БД, отсортированных по дате создания.
    """
    # Используем SQLAlchemy 2.0 style select для асинхронной работы
    result = await db.execute(
        select(Message).order_by(Message.created_at.desc())
    )
    # result.scalars().all() возвращает список объектов Message
    return result.scalars().all()