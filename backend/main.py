# main.py
from fastapi import FastAPI, Depends
# Теперь импортируем только то, что нужно
from .database import get_db, create_db_and_tables # <-- Добавьте create_db_and_tables
from . import crud, ai, schemas
from sqlalchemy.ext.asyncio import AsyncSession

app = FastAPI()

@app.on_event("startup")
async def startup():
    # Используем новую функцию для создания файла БД и таблицы
    await create_db_and_tables() 
    print("Database and tables created successfully!")

# ... остальной код роутов остается прежним

@app.post("/analyze")
async def analyze(payload: schemas.MessageCreate, db: AsyncSession = Depends(get_db)):
    text = payload.text
    classification = ai.classify_text(text)
    answer = ai.generate_answer(classification, text)

    msg = await crud.create_message(db, text, classification, answer)
    return msg

@app.get("/messages")
async def list_messages(db: AsyncSession = Depends(get_db)):
    return await crud.get_messages(db)
