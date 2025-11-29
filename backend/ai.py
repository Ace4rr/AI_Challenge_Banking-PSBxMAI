def classify_text(text: str) -> str:
    t = text.lower()
    if any(word in t for word in ["жалоба", "претензия", "недовольство", "ошибка"]):
        return "Официальная жалоба"
    if any(word in t for word in ["пожалуйста", "можно ли", "хочу уточнить", "запрос"]):
        return "Запрос информации"
    if any(word in t for word in ["срочно", "немедленно", "оперативно"]):
        return "Срочный запрос"
    return "Общее письмо"
def detect_sla(classification: str) -> str:
    if classification == "Официальная жалоба":
        return "high" 
    if classification == "Срочный запрос":
        return "critical"
    if classification == "Запрос информации":
        return "medium"
    return "low"

def detect_tone(user_role: str) -> str:
    role = user_role.lower()
    if role == "admin":
        return "strict-formal" 
    if role == "manager":
        return "formal"          
    if role == "employee":
        return "corporate" 
    if role == "partner":
        return "semi-formal"   
    return "neutral"  
def generate_answer(classification: str, text: str, tone: str) -> str:
    tone_prefix = {
        "strict-formal": "Уважаемый коллега, информируем вас о том, что ",
        "formal": "Уважаемый клиент, сообщаем, что ",
        "corporate": "Коллега, фиксируем, что ",
        "semi-formal": "Здравствуйте! Благодарим вас за обращение. ",
        "neutral": "Спасибо за ваше сообщение! "
    }
    prefix = tone_prefix.get(tone, "Спасибо за обращение! ")
    if classification == "Официальная жалоба":
        core = "ваша жалоба принята в работу, и мы приступили к её рассмотрению."
    elif classification == "Срочный запрос":
        core = "ваш запрос обработан в приоритетном порядке, мы свяжемся с вами в ближайшее время."
    elif classification == "Запрос информации":
        core = "мы получили ваш запрос и готовим развернутый ответ."
    else:
        core = "мы приняли ваше обращение и свяжемся с вами в ближайшее время."

    return prefix + core

def process_message(text: str, user_role: str) -> dict:

    classification = classify_text(text)
    sla = detect_sla(classification)
    tone = detect_tone(user_role)
    answer = generate_answer(classification, text, tone)
    return {
        "classification": classification,
        "sla": sla,
        "tone": tone,
        "answer": answer
    }
