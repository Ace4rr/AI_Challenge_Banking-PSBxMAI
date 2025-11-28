from fastapi import FastAPI, Depends
from .database import engine, Base, get_db
from . import crud, ai, schemas
from sqlalchemy.ext.asyncio import AsyncSession

app = FastAPI()

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

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
