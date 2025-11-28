# main.py
from fastapi import FastAPI, Depends
# НОВЫЙ ИМПОРТ:
from contextlib import asynccontextmanager 
# Теперь импортируем из database только get_db и create_db_and_tables
from .database import get_db, create_db_and_tables 
from . import crud, ai, schemas
from sqlalchemy.ext.asyncio import AsyncSession

# 1. Используем менеджер контекста для жизненного цикла приложения
@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- КОД ЗАПУСКА (СТАРТАП) ---
    await create_db_and_tables() 
    print("Database and tables created successfully!")
    
    yield # Приложение начинает принимать запросы
    
    # --- КОД ОСТАНОВКИ (ШАТДАУН) ---
    print("Application shutting down...")

# 2. Инициализируем FastAPI с аргументом lifespan
app = FastAPI(lifespan=lifespan) 


# --- РОУТЫ ОСТАЮТСЯ БЕЗ ИЗМЕНЕНИЙ ---

@app.post("/analyze")
async def analyze(payload: schemas.MessageCreate,user_id:int, db: AsyncSession = Depends(get_db)):
    text = payload.text
    classification = ai.classify_text(text)
    answer = ai.generate_answer(classification, text)

    msg = await crud.create_message(db, text, classification, answer)
    msg.user_id=user_id
    await db.commit()
    return msg

@app.post("/register",response_model=schemas.UserOut)
async def register(user: schemas.UserCreate, db: AsyncSession=Depends(get_db)):
    if existing:
        return{"error":"User already exists"}
    new_user=await crud.create_user(db,user.username,user.email,user.password)
    return new_user

@app.post("/login")
async def login(user: schemas.UserCreate,db:AsyncSession=Depends(get_db)):
    auth_user=await crud.authenticate_user(db,user.username,user.password)
    if not auth_user:   
        return{"error":"Invalid username or password"}
    return {"message":"Login succesful","user_id":auth_user.id}

@app.get("/messages")
async def list_messages(db: AsyncSession = Depends(get_db)):
    return await crud.get_messages(db)