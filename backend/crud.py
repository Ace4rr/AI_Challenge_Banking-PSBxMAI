from sqlalchemy.ext.asyncio import AsyncSession
from . import models, schemas
from sqlalchemy import select

async def create_message(db: AsyncSession, text: str, classification: str, answer: str):
    msg = models.Message(input_text=text, classification=classification, generated_answer=answer)
    db.add(msg)
    await db.commit()
    await db.refresh(msg)
    return msg

async def get_messages(db: AsyncSession, limit: int = 100):
    q = select(models.Message).order_by(models.Message.created_at.desc()).limit(limit)
    res = await db.execute(q)
    return res.scalars().all()