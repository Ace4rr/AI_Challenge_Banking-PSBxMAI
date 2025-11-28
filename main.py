import os
import json
import requests
import warnings
from io import BytesIO
from dotenv import load_dotenv
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Импорты для парсинга
from pypdf import PdfReader
from docx import Document
from gigachat import GigaChat

try:
    requests.packages.urllib3.disable_warnings()
    warnings.filterwarnings("ignore")
except Exception:
    pass

def extract_text_from_pdf(file_bytes: bytes) -> str:
    """Извлекает текст из PDF-файла, используя pypdf."""
    try:
        pdf_file = BytesIO(file_bytes)
        reader = PdfReader(pdf_file)
        text = ""
        for page in reader.pages:
            if page.extract_text():
                text += page.extract_text() + "\n"
        return text
    except Exception as e:
        return f"Парсинг PDF не удался: {e}"

def extract_text_from_docx(file_bytes: bytes) -> str:
    """Извлекает текст из DOCX-файла, используя python-docx."""
    try:
        document = Document(BytesIO(file_bytes))
        text = "\n".join([paragraph.text for paragraph in document.paragraphs])
        return text
    except Exception as e:
        return f"Парсинг DOCX не удался: {e}"


load_dotenv()

gigachat_client = None
try:
    GIGACHAT_KEY = "MDE5YWNhODEtNTE1Yy03ZmJmLTg2MmEtZDg0YzFiOGExODZlOmE3Zjc4MDdkLTRjOTgtNGFkOC1iOTFkLWRjNWY1NzExYTAyNA=="
    
    if GIGACHAT_KEY:
        print("Инициализация GigaChat клиента...")
        gigachat_client = GigaChat(
            credentials=GIGACHAT_KEY,
            profanity=False,
            ssl_verify=False,
            verify_ssl_certs=False,
            verify_ssl=False
        )
    else:
        print("WARNING: GIGACHAT_API_KEY not set. Using test data.")

except Exception as e:
    print(f"Ошибка инициализации GigaChat: {e}")

class AIResponse(BaseModel):
    """Модель структурированного ответа от AI."""
    category: str
    reply_draft: str
    summary: str


app = FastAPI(
    title="GigaChat Banking Assistant",
    description="Backend для автоматической сортировки и ответа на почту",
    version="1.0.0"
)

origins = [
    "http://localhost:5173",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"], 
)


@app.post("/analyze_email", response_model=AIResponse)
async def analyze_email_with_gigachat(file: UploadFile = File(...)):
    """Принимает файл, извлекает текст и отправляет его в GigaChat."""
    
    # 1. Чтение и Парсинг Файла
    try:
        file_contents = await file.read()
    except Exception:
        raise HTTPException(status_code=400, detail="Не удалось прочитать файл.")
    
    file_name = file.filename.lower()
    
    if file_name.endswith(('.txt', '.eml')):
        email_content = file_contents.decode("utf-8", errors="ignore")
    elif file_name.endswith('.pdf'):
        email_content = extract_text_from_pdf(file_contents)
    elif file_name.endswith('.docx'):
        email_content = extract_text_from_docx(file_contents)
    else:
        raise HTTPException(status_code=400, detail="Неподдерживаемый формат файла.")

    if not email_content or email_content.startswith("Парсинг"):
        raise HTTPException(status_code=400, detail="Не удалось извлечь текст из файла.")


    # 2. Формирование промта
    system_prompt = """
    Ты — умный ассистент банка, твой ответ будет использоваться для мгновенного ответа клиенту.
    Проанализируй входящее письмо. 
    1. Определи категорию (JSON Key: "category") строго из списка: 'Предложение о партнерстве', 'Жалоба на сервис', 'Запрос на кредит', 'Предложение о работе банку', 'Спам'.
    2. Напиши вежливый, официальный, но краткий черновик ответа (JSON Key: "reply_draft"), используя официальный тон банка.
    3. Создай краткое резюме (JSON Key: "summary") письма для внутреннего использования.
    
    Верни ответ СТРОГО в формате JSON с ТОЛЬКО этими тремя ключами: "category", "reply_draft", "summary". Не добавляй никаких пояснений или дополнительного текста вне JSON.
    """
    
    # Объединение промптов
    full_prompt = f"""
    {system_prompt}
    
    --- ДАННЫЕ ДЛЯ АНАЛИЗА ---
    
    Текст письма:
    {email_content}
    """
        

    try:
        # 4. Вызов GigaChat API
        response = gigachat_client.chat(full_prompt)
        
        ai_response_str = response.choices[0].message.content

        ai_response_str = ai_response_str.strip()
        

        if ai_response_str.startswith("```json"):
            ai_response_str = ai_response_str[len("```json"):].strip()
            

        if ai_response_str.endswith("```"):
            ai_response_str = ai_response_str[:-len("```")].strip()
            

        result_data = json.loads(ai_response_str)

        # 6. Валидация и возврат
        return AIResponse(
            category=result_data.get("category", "Ошибка классификации"),
            reply_draft=result_data.get("reply_draft", "Ошибка генерации ответа."),
            summary=result_data.get("summary", "Ошибка генерации резюме.")
        )
        
    except json.JSONDecodeError:
        print(f"GigaChat вернул невалидный JSON: {ai_response_str}")
        raise HTTPException(
            status_code=500, 
            detail=f"AI вернул невалидный JSON. Полученный текст: {ai_response_str[:200]}..."
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Ошибка связи с GigaChat: {e}"
        )