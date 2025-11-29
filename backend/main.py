# backend/main.py

import sys
import os
import json # Новый импорт для работы с JSON

# =================================================================
# !!! КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: ПРИНУДИТЕЛЬНОЕ ДОБАВЛЕНИЕ ПУТЕЙ !!!
# Это обходит ModuleNotFoundError (gigachain) на Windows
# =================================================================
try:
    # 1. Получаем корень проекта: .../AI_Challenge_Banking-PSBxMAI
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    
    # 2. Добавляем корень проекта для правильной работы относительных импортов
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
        print(f"✅ Проектный путь: {project_root} принудительно добавлен в sys.path.")
        
    # 3. Проверяем ОБА возможных пути к site-packages в venv и добавляем рабочий
    
    # Путь 1 (Стандартный для большинства Python 3.x на Windows)
    venv_site_packages_lib = os.path.join(project_root, 'venv', 'Lib', 'site-packages')
    
    # Путь 2 (Если папка Lib отсутствует)
    venv_site_packages_nolib = os.path.join(project_root, 'venv', 'site-packages')
    
    if os.path.exists(venv_site_packages_lib):
        if venv_site_packages_lib not in sys.path:
            sys.path.insert(0, venv_site_packages_lib)
            print(f"✅ Venv Lib путь: {venv_site_packages_lib} принудительно добавлен в sys.path.")
    elif os.path.exists(venv_site_packages_nolib):
        if venv_site_packages_nolib not in sys.path:
            sys.path.insert(0, venv_site_packages_nolib)
            print(f"✅ Venv NoLib путь: {venv_site_packages_nolib} принудительно добавлен в sys.path.")

except Exception as e:
    print(f"❌ Ошибка при попытке исправить путь sys.path: {e}")
# =================================================================

from fastapi import FastAPI, Depends, UploadFile, File, HTTPException 
from contextlib import asynccontextmanager 
from .database import get_db, create_db_and_tables 
from . import crud, ai, schemas
from .file_utils import extract_text_from_file
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.middleware.cors import CORSMiddleware 

# --- 1. Менеджер контекста для жизненного цикла приложения ---

@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_db_and_tables() 
    print("Database and tables created successfully!")
    
    # Дополнительная проверка, что GigaChat инициализирован
    from .ai import llm
    if llm is not None:
        print("GigaChat клиент успешно инициализирован.")
    
    yield
    print("Application shutting down...")

# --- 2. Инициализация FastAPI и остальные роуты (без изменений) ---

app = FastAPI(lifespan=lifespan) 

origins = ["http://localhost:8080"] 

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 4. Роут POST /analyze (Текст) ---

@app.post("/analyze", response_model=schemas.MessageOut)
async def analyze(payload: schemas.MessageCreate, db: AsyncSession = Depends(get_db)):
    text = payload.text
    
    # 1. Единый вызов для комплексного анализа
    try:
        analysis_result = ai.analyze_correspondence(text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка AI-анализа: {e}")

    # 2. Сохранение в БД. 
    # ВНИМАНИЕ: Предполагается, что crud.create_message в crud.py был обновлен 
    # для приема всех этих новых параметров.
    msg = await crud.create_message(
        db, 
        text, 
        # Старые поля
        analysis_result.get("category", "Не определено"), # Заменяет classification
        analysis_result.get("official_reply", "Ошибка генерации ответа."), # Заменяет answer
        json.dumps(analysis_result.get("parameters", {})), # Заменяет extracted_data
        
        # Новые поля
        analysis_result.get("reply_style", "Не определено"),
        analysis_result.get("time_to_reply", "Не определено"),
        analysis_result.get("summary", "Нет резюме."),
        analysis_result.get("infrastructure_sphere", "Не определено"),
        analysis_result.get("risks_and_fixes", "Нет рисков."),
    )
    return msg

# --- 5. Роут GET /history (История) ---

@app.get("/history", response_model=list[schemas.MessageOut])
async def get_history(db: AsyncSession = Depends(get_db)):
    messages = await crud.get_messages(db)
    return messages

# --- 6. Роут POST /analyze_file (Файл) ---
@app.post("/analyze_file", response_model=schemas.MessageOut)
async def analyze_file(
    file: UploadFile = File(...), 
    db: AsyncSession = Depends(get_db)
):
    """Принимает файл (PDF или TXT), извлекает текст и анализирует его."""
    
    try:
        text = extract_text_from_file(file)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка обработки файла: {e}")

    # 1. Единый вызов для комплексного анализа
    try:
        analysis_result = ai.analyze_correspondence(text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка AI-анализа: {e}")


    # 2. Сохранение в БД. 
    # ВНИМАНИЕ: Предполагается, что crud.create_message в crud.py был обновлен 
    # для приема всех этих новых параметров.
    msg = await crud.create_message(
        db, 
        text, 
        # Старые поля
        analysis_result.get("category", "Не определено"), # Заменяет classification
        analysis_result.get("official_reply", "Ошибка генерации ответа."), # Заменяет answer
        json.dumps(analysis_result.get("parameters", {})), # Заменяет extracted_data
        
        # Новые поля
        analysis_result.get("reply_style", "Не определено"),
        analysis_result.get("time_to_reply", "Не определено"),
        analysis_result.get("summary", "Нет резюме."),
        analysis_result.get("infrastructure_sphere", "Не определено"),
        analysis_result.get("risks_and_fixes", "Нет рисков."),
    )
    return msg