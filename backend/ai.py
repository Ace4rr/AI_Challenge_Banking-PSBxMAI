import os
import json
from dotenv import load_dotenv
import re # <-- Добавлен для надежного парсинга JSON
from typing import Dict, Any

from gigachat import GigaChat 
import requests 
import warnings

# --- СИСТЕМНЫЕ НАСТРОЙКИ И ОБХОДЫ SSL ---
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

# --- КОНФИГУРАЦИЯ GIGACHAT ---
load_dotenv() 

GIGACHAT_API_KEY = os.getenv("GIGACHAT_API_KEY")

if not GIGACHAT_API_KEY:
    print("!!! ВНИМАНИЕ: Переменная GIGACHAT_API_KEY не найдена. AI будет использовать заглушки. !!!")

llm = None 
if GIGACHAT_API_KEY:
    try:
        # Убраны устаревшие/отклоненные параметры (profanity, ssl_verify, verify_ssl_certs)
        llm = GigaChat(profanity=False,
        ssl_verify=False,
        verify_ssl_certs=False,
            credentials=GIGACHAT_API_KEY,
            model="GigaChat-Pro",
        )
        print("GigaChat клиент успешно инициализирован.")
    except Exception as e:
        llm = None
        print(f"!!! Ошибка инициализации GigaChat: {e}. AI будет использовать заглушки. !!!")


# --- ГЛАВНЫЙ СИСТЕМНЫЙ ПРОМТ ДЛЯ КОМПЛЕКСНОГО АНАЛИЗА ---
SYSTEM_PROMPT = """
Ты — ассистент банка ПСБ (Промсвязьбанк), один из умнейших людей на планете, максимально вежливый и терпимый к другим человек. Тебя взяли на работу в отдел банка ПСБ... (Остальной текст пролога)

1. Определи категорию (JSON Key: "category") строго из списка: "Запрос информации/документов", "Официальная жалоба/претензия", "Регуляторный запрос", "Партнерское предложение", "Запрос на согласование", "Уведомление или информирование", "Спам/рассылка", "Неуместное сообщение", "Вопросы от клиентов".
2. В зависимости от настроя собеседника и темы сообщения определи уместный для ответа стиль написания текста (JSON Key: "reply_style"), выбрав из данного списка: Строгий официальный (для регуляторов и государственных органов), Деловой корпоративный (для партнёров и контрагентов), Клиентоориентированный (для физических и юридических лиц), Краткий информационный (для простых запросов).
3. Проведи глубокий анализ полученного тобой текста письма. Выдели ключевые параметры (JSON Key: "parameters"). Используй **КРАТКИЕ, ПРОСТЫЕ КЛЮЧИ** (например, "email_отправителя", "ФЗ_основание"). **В качестве значения** укажи текст из письма и пояснение в скобках. **Строго запрещается** использовать в ключах или значениях двоеточия, двойные кавычки (кроме обрамляющих) или символы перевода строки. Пример: **"EmailОтправителя": "Petrov-Ivan@sigma-holding.ru (Почтовый адрес отправителя)"**, **"НормативныйАкт": "Федеральный закон № 44-ФЗ (Нормативный акт для обеспечения)"**.
4. На основании информации из письма, его типа, нормативных требований, а также темы и тона отправителя, определи требуемое время для составления ответа (так называемый "дедлайн", в течение которого он должен быть написан). (JSON Key: "time_to_reply")
5. Создай краткое резюме (JSON Key: "summary") письма, а именно: что хочет от клиента его отправитель (его требования и ожидания).
6. На основе темы письма и требований отправителя определи одно из необходимых подразделений для согласования письма (например: "Отдел льготного кредитования", "Бухгалтерия") (JSON Key: "infrastructure_sphere").
7. Обработав все вышеперечисленные пункты, напиши максимально вежливый и презентабельный ответ на письмо (JSON Key: "official_reply"), используя официальный тон банка и при этом соблюдая стиль+длину написания текста из п. 2. Ответ должен выглядеть, как официальное письмо и быть полностью готовым к отправке человеку. Его длина не должна быть меньше 1/2 длины исходного письма, но при этом и не быть слишком огромной. При написании письма (если нужно!) ссылайся на нормативные акты РФ, уставы Центробанка РФ, Федеральные законы, Конституцию РФ.
8. В отдельном абзаце максимально подробно опиши потенциальные риски, которые могут возникнуть при отправке данного сообщения. Выдели нормативные акты, на которые ссылался отправитель сообщения. Напиши, что конкретно следовало бы перепроверить и подправить перед тем, как составлять финальное ответное письмо. (JSON Key: "risks_and_fixes")

Верни ответ СТРОГО в формате JSON с ТОЛЬКО этими ключами: "category", "reply_style", "parameters", "time_to_reply", "summary", "infrastructure_sphere", "official_reply", "risks_and_fixes". Не добавляй никаких пояснений или дополнительного текста вне JSON.
"""

# --- ГЛАВНАЯ ФУНКЦИЯ АНАЛИЗА ---
def analyze_correspondence(text: str) -> Dict[str, Any]:
    """
    Отправляет полный текст письма в GigaChat для комплексного анализа по 8 пунктам 
    и возвращает структурированный JSON-ответ.
    """
    if llm is None:
        # Возвращаем заглушку, соответствующую ожидаемой структуре
        return {
            "category": "Общее письмо (ЗАГЛУШКА)",
            "reply_style": "Краткий информационный",
            "parameters": "{}",
            "time_to_reply": "1 рабочий день",
            "summary": "AI клиент не инициализирован. Используется заглушка.",
            "infrastructure_sphere": "Отдел технической поддержки",
            "official_reply": "Уважаемый клиент! В настоящий момент система искусственного интеллекта недоступна для обработки Вашего запроса. Пожалуйста, обратитесь к нашему менеджеру.",
            "risks_and_fixes": "Риски: сообщение не обработано. Исправления: активировать GigaChat API.",
        }

    full_prompt = f"""
    {SYSTEM_PROMPT}
    
    --- ДАННЫЕ ДЛЯ АНАЛИЗА (Текст письма) ---
    
    {text}
    """
    
    try:
        response = llm.chat(full_prompt) 
        ai_response_str = response.choices[0].message.content.strip()

        # 1. Поиск и извлечение чистого JSON с помощью regex (наиболее надежный способ)
        # Ищем блок, начинающийся с { и заканчивающийся на }.
        json_match = re.search(r'\{.*\}', ai_response_str, re.DOTALL)
        
        if json_match:
            json_string = json_match.group(0).strip()
        else:
            # Fallback: Если JSON не найден, попробуем очистку от маркеров Markdown 
            json_string = ai_response_str
            if json_string.startswith("```json"):
                json_string = json_string[len("```json"):].strip()
            if json_string.endswith("```"):
                json_string = json_string[:-len("```")].strip()
        
        # Если после всех попыток строка пуста, выбрасываем ошибку
        if not json_string.strip():
             raise json.JSONDecodeError("JSON string is empty after cleaning.", ai_response_str, 0)

        # 2. Парсинг и возврат JSON
        result_data = json.loads(json_string)
        return result_data

    except json.JSONDecodeError as e:
        print(f"Ошибка парсинга JSON от GigaChat. Полученный текст (начало): {ai_response_str[:500]}...")
        # Сохраняем исходный текст в исключение, чтобы увидеть, что вернул GigaChat
        raise Exception(f"GigaChat вернул невалидный JSON. Ошибка: {e}. Полученный текст: {ai_response_str}")
    
    except Exception as e:
        print(f"Ошибка выполнения запроса GigaChat: {e.__class__.__name__} ({e})")
        raise Exception(f"Ошибка GigaChat: {e.__class__.__name__}")