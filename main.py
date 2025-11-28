import os
import json
from dotenv import load_dotenv
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
# from gigachat import GigaChat # Раскомментировать, когда вы получите библиотеку GigaChat

# ----------------------------------------------------
# 1. КОНФИГУРАЦИЯ БЕЗОПАСНОСТИ (GIGACHAT)
# ----------------------------------------------------

load_dotenv()

# Инициализация GigaChat клиента (используем заглушку, пока не настроен ключ)
# В РЕАЛЬНОМ ПРОЕКТЕ: здесь будет инициализация GigaChat, настроенная на ваш 
# локальный (on-premise) endpoint, как мы обсуждали ранее.

gigachat_client = None
try:
    GIGACHAT_KEY = os.getenv("GIGACHAT_API_KEY")
    if GIGACHAT_KEY:
        # gigachat_client = GigaChat(credentials=GIGACHAT_KEY, verify_ssl=False)
        # ВРЕМЕННАЯ ЗАГЛУШКА для тестирования:
        print("GigaChat key found, but client is temporarily disabled for testing.")
        pass 
    else:
        print("WARNING: GIGACHAT_API_KEY not set. Using test data.")

except Exception as e:
    print(f"Ошибка инициализации GigaChat: {e}")

# ----------------------------------------------------
# 2. МОДЕЛИ ДАННЫХ (Pydantic)
# ----------------------------------------------------

class AIResponse(BaseModel):
    """Модель структурированного ответа от AI."""
    category: str
    reply_draft: str
    summary: str

# ----------------------------------------------------
# 3. НАСТРОЙКА FASTAPI И CORS
# ----------------------------------------------------

app = FastAPI(
    title="GigaChat Banking Assistant",
    description="Backend для автоматической сортировки и ответа на почту",
    version="1.0.0"
)

# КОНФИГУРАЦИЯ CORS
# Добавляем ваш React-порт (5173), чтобы избежать "Network Error"
origins = [
    "http://localhost:5173",  # Порт, на котором у вас сейчас запущен React (Vite)
    "http://localhost:3000",  # Стандартный порт для React (create-react-app)
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"], 
)

# ----------------------------------------------------
# 4. ОСНОВНОЙ ЭНДПОИНТ (с обработкой файла)
# ----------------------------------------------------

@app.post("/analyze_email", response_model=AIResponse)
async def analyze_email_with_gigachat(file: UploadFile = File(...)):
    """Принимает файл, извлекает текст и отправляет его в GigaChat."""
    
    # 1. Чтение файла
    try:
        file_contents = await file.read()
        
        # NOTE: Здесь должен быть код парсинга PDF/DOCX в зависимости от file.filename
        
        # Предполагаем, что это текстовый файл (txt, eml)
        email_content = file_contents.decode("utf-8", errors="ignore")
        
    except Exception as e:
        raise HTTPException(
            status_code=400, 
            detail=f"Не удалось прочитать файл: {e}"
        )

    # 2. Формирование PROMPT
    # ... (Тот же промпт, что и раньше)
    
    # ВРЕМЕННАЯ ЗАГЛУШКА для проверки соединения с React
    if not gigachat_client:
        test_content = f"Анализ письма: '{email_content[:50]}...'"
        
        # Если GigaChat не настроен, возвращаем тестовый ответ
        return AIResponse(
            category="Жалоба (ТЕСТ)",
            reply_draft=f"Уважаемый клиент! Мы получили ваше письмо. {test_content} Спасибо за обращение!",
            summary=f"Письмо успешно прочитано. Тестовый анализ: {test_content}"
        )

    # 3. Вызов GigaChat API (будет активирован, когда ключ будет настроен)
    # ... (логика вызова gigachat_client.chat)
    
    # ... (логика возврата реального AIResponse)