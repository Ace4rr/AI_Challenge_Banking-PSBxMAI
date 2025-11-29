# backend/main.py

from fastapi import FastAPI, Depends, UploadFile, File, HTTPException # ДОБАВЛЕНЫ UploadFile, File, HTTPException
from contextlib import asynccontextmanager 
from .database import get_db, create_db_and_tables 
from . import crud, ai, schemas
from .file_utils import extract_text_from_file # ИМПОРТ НОВОГО МОДУЛЯ
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.middleware.cors import CORSMiddleware # Импорт для CORS

# --- 1. Менеджер контекста для жизненного цикла приложения (создание БД) ---

@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- КОД ЗАПУСКА (СТАРТАП) ---
    await create_db_and_tables() 
    print("Database and tables created successfully!")
    
    yield # Приложение начинает принимать запросы
    
    # --- КОД ОСТАНОВКИ (ШАТДАУН) ---
    print("Application shutting down...")

# --- 2. Инициализация FastAPI с жизненным циклом ---

app = FastAPI(lifespan=lifespan) 

# --- 3. Настройка CORS (ОБЯЗАТЕЛЬНО для работы с фронтендом) ---

origins = ["http://localhost:8080"] 

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 4. Роут POST /analyze (Отправка нового сообщения в виде текста) ---

@app.post("/analyze", response_model=schemas.MessageOut)
async def analyze(payload: schemas.MessageCreate, db: AsyncSession = Depends(get_db)):
    text = payload.text
    
    # 1. Классификация и генерация ответа
    classification = ai.classify_text(text)
    answer = ai.generate_answer(classification, text)

    # 2. Сохранение в БД
    msg = await crud.create_message(db, text, classification, answer)
    return msg

# --- 5. Роут GET /history (Получение истории) ---

@app.get("/history", response_model=list[schemas.MessageOut])
async def get_history(db: AsyncSession = Depends(get_db)):
    messages = await crud.get_messages(db)
    return messages

# --- 6. НОВЫЙ РОУТ: POST /analyze_file (Отправка файла) ---
@app.post("/analyze_file", response_model=schemas.MessageOut)
async def analyze_file(
    file: UploadFile = File(...), 
    db: AsyncSession = Depends(get_db)
):
    """Принимает файл (PDF или TXT), извлекает текст и анализирует его."""
    
    # 1. Извлечение текста из файла
    # Если extract_text_from_file вызывает HTTPException, FastAPI автоматически его перехватит.
    try:
        text = extract_text_from_file(file)
    except Exception as e:
        # Для ошибок, не являющихся HTTPException, возвращаем 500
        raise HTTPException(status_code=500, detail=f"Внутренняя ошибка сервера при обработке файла: {e}")

    # 2. Классификация и генерация ответа (используется существующая логика)
    classification = ai.classify_text(text)
    answer = ai.generate_answer(classification, text)

    # 3. Сохранение в БД
    # В БД сохраняем извлеченный текст
    msg = await crud.create_message(db, text, classification, answer)
    
    return msg