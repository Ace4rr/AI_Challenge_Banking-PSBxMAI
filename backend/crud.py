from sqlalchemy.ext.asyncio import AsyncSession
from . import models, schemas
from sqlalchemy import select

async def create_message(db: AsyncSession, user_id: int, text: str, classification: str, answer: str):
    msg = models.Message(input_text=text, classification=classification, generated_answer=answer, user_id=user_id)
    db.add(msg)
    await db.commit()
    await db.refresh(msg)
    return msg

async def create_user(db: AsyncSession, username: str, email: str, password: str):
    user = models.User(username=username,enail=email,password=password)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user 

async def get_user_by_username(db: AsyncSession, username: str):
    result = await db.execute(select(models.User).where(models.User.username==username))
    return result.scalar_one_or_none()

async def get_messages_by_user(db: AsyncSession, user_id: int):
    q = select(models.Message).where(models.Message.user_id==user_id).order_by(models.Message.created_at.desc())
    res = await db.execute(q)
    return res.scalars().all()

async def authenticate_user(db: AsyncSession, username: str, password: str):
    user=await get_user_by_username(db,username)
    if user and user.password==password:
        return user
    return None

async def get_messages(db: AsyncSession, limit: int = 100):
    q = select(models.Message).order_by(models.Message.created_at.desc()).limit(limit)
    res = await db.execute(q)
    return res.scalars().all()