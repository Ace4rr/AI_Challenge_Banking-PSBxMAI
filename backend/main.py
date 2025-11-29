# backend/main.py
from fastapi import FastAPI, Depends
from contextlib import asynccontextmanager 
from .database import get_db, create_db_and_tables 
from . import crud, ai, schemas
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.middleware.cors import CORSMiddleware 

# --- 1. Менеджер контекста для жизненного цикла приложения (создание БД) ---

@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- КОД ЗАПУСКА (СТАРТАП) ---
    await create_db_and_tables() 
    print("Database and tables created successfully!")
    
    yield
    
    # --- КОД ОСТАНОВКИ (ШАТДАУН) ---
    print("Application shutting down...")

# --- 2. Инициализация FastAPI с жизненным циклом ---

app = FastAPI(lifespan=lifespan) 

# --- 3. Настройка CORS (ИСПРАВЛЕНО ДЛЯ РЕШЕНИЯ ПРОБЛЕМЫ БРАУЗЕРА) ---

# Разрешаем localhost и 127.0.0.1 на порту 8080
origins = ["http://localhost:8080", "http://127.0.0.1:8080"] 

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 4. Роут POST /analyze (Отправка нового сообщения) ---

@app.post("/analyze", response_model=schemas.MessageOut)
async def analyze(payload: schemas.MessageCreate, db: AsyncSession = Depends(get_db)):
    text = payload.text
    
    classification = ai.classify_text(text)
    answer = ai.generate_answer(classification, text)

    msg = await crud.create_message(db, text, classification, answer)
    
    return msg

# --- 5. Роут GET /history (Загрузка истории чата) ---

@app.get("/history", response_model=list[schemas.MessageOut])
async def get_chat_history(db: AsyncSession = Depends(get_db)):
    """Получает последние 100 сообщений из базы данных."""
    messages = await crud.get_messages(db, limit=100)
    return messages