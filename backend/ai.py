import os
import json
from dotenv import load_dotenv


from gigachat import GigaChat 

import requests 
import warnings

requests_session = requests.Session()
requests_session.verify = False 

try:
    requests.packages.urllib3.disable_warnings()
    warnings.filterwarnings(
        "ignore", 
        category=requests.packages.urllib3.exceptions.InsecureRequestWarning
    )
except Exception:
    pass


os.environ['PYTHONHTTPSVERIFY'] = '0' 


load_dotenv() 

GIGACHAT_API_KEY = os.getenv("GIGACHAT_API_KEY")

if not GIGACHAT_API_KEY:
    print("!!! ВНИМАНИЕ: Переменная GIGACHAT_API_KEY не найдена. AI будет использовать заглушки. !!!")

llm = None 
if GIGACHAT_API_KEY:
    try:
        llm = GigaChat( 
            credentials=GIGACHAT_API_KEY,
            model="GigaChat-Pro",
        )
        print("GigaChat клиент успешно инициализирован (СЕЙЧАС ДОЛЖНО РАБОТАТЬ).")
    except Exception as e:
        llm = None
        print(f"!!! Ошибка инициализации GigaChat: {e}. AI будет использовать заглушки. !!!")
    
def _call_gigachat(system_prompt: str, user_text: str) -> str:
    """Отправляет запрос в GigaChat, используя объединенный строковый промпт."""
    if llm is None: 
        raise Exception("GigaChat клиент не инициализирован.")

    full_prompt = f"""
    {system_prompt}
    
    --- ДАННЫЕ ДЛЯ АНАЛИЗА ---
    
    {user_text}
    """
    
    response = llm.chat(full_prompt) 
    return response.choices[0].message.content.strip()

def classify_text(text: str) -> str:
    if llm is None:
        t = text.lower()
        if "жалоба" in t or "претензия" in t:
            return "Официальная жалоба (ЗАГЛУШКА)"
        if "запрос" in t or "пожалуйста" in t:
            return "Запрос информации (ЗАГЛУШКА)"
        return "Общее письмо (ЗАГЛУШКА)"

    classification_template = """
    Ты - ассистент по классификации обращений в банке. 
    Твоя задача - проанализировать текст обращения клиента и выбрать одну из трех категорий:
    1. Официальная жалоба
    2. Запрос информации
    3. Общее письмо
    
    Отвечай строго только одним словом, соответствующим выбранной категории. Не добавляй никаких пояснений, знаков препинания или дополнительных слов.
    """

    try:
        result = _call_gigachat(
            system_prompt=classification_template, 
            user_text=f"Текст обращения: {text}\nКатегория:"
        )
        
        valid_categories = ["Официальная жалоба", "Запрос информации", "Общее письмо"]
        for category in result.split(): 
            if category in valid_categories:
                return category
        
        return "Общее письмо" 

    except Exception as e:
        print(f"Ошибка при классификации с GigaChat: {e.__class__.__name__} ({e})") 
        return "Общее письмо (ОШИБКА GIGACHAT)"

def generate_answer(classification: str, text: str) -> str:
    if llm is None:
        if "жалоба" in classification:
            return "Спасибо за обращение. Ваша жалоба зарегистрирована и будет рассмотрена в кратчайшие сроки (ЗАГЛУШКА)."
        if "запрос" in classification:
            return "Спасибо. Подготавливаем ответ на ваш запрос, ожидайте обратной связи (ЗАГЛУШКА)."
        return "Спасибо за обращение. Мы свяжемся с вами в ближайшее время (ЗАГЛУШКА)."
        
    answer_template = f"""
    Ты - вежливый и компетентный сотрудник службы поддержки банка. 
    Тебе поступило обращение клиента, которое было классифицировано как: **{classification}**.
    
    На основе оригинального текста обращения, напиши короткий, профессиональный и вежливый ответ клиенту (не более 4-х предложений).
    """

    try:
        return _call_gigachat(
            system_prompt=answer_template, 
            user_text=f"Оригинальный текст обращения: {text}\nТвой ответ:"
        )
    except Exception as e:
        print(f"Ошибка при генерации ответа с GigaChat: {e.__class__.__name__} ({e})") 
        return "Произошла ошибка при генерации ответа через GigaChat: ConnectError"

def extract_entities(text: str) -> str:
    """Извлекает сущности (ФИО, номер счета, дату, сумму) в JSON-формате."""

    if llm is None:
        return "{}"

    extraction_template = """
    Ты - ассистент по извлечению структурированных данных из текста. 
    Твоя задача - извлечь из текста следующие сущности, если они присутствуют:
    - ФИО клиента
    - Номер счета (если указан)
    - Сумма (если указана)
    - Дата события (если указана)
    
    Результат должен быть строго в формате JSON. Если сущность не найдена, используй значение null.
    
    Пример ожидаемого JSON-формата:
    {
      "ФИО_клиента": "Иванов Иван Иванович",
      "Номер_счета": "40817810000000000001",
      "Сумма": "50000 рублей",
      "Дата_события": "12.03.2024"
    }

    """
    
    try:
        json_string = _call_gigachat(
            system_prompt=extraction_template,
            user_text=f"Текст обращения: {text}\nJSON:"
        )

        if json_string.startswith("```json"):
            json_string = json_string[len("```json"):].strip()
        
        if json_string.endswith("```"):
            json_string = json_string[:-len("```")].strip()
        
        json.loads(json_string) 

        return json_string

    except json.JSONDecodeError:
        print(f"GigaChat вернул невалидный JSON для извлечения сущностей: {json_string[:100]}...")
        return "{}"
    except Exception as e:
        print(f"Ошибка при извлечении сущностей с GigaChat: {e.__class__.__name__} ({e})")
        return "{}"