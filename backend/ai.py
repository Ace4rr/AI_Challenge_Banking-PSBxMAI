def classify_text(text: str) -> str:
    t = text.lower()
    if "жалобы" in t or "претензии" in t:
        return "Официальная жалоба"
    if "запрос" in t or "пожалуйста" in t:
        return "Запрос информации"
    return "Общее письмо"
#Сейчас это заглушка(нейрослоп)!!
def generate_answer(classification: str, text: str) -> str:
    if classification == "Официальная жалоба":
        return "Спасибо за обращение. Ваша жалоба зарегистрирована..."
    if classification == "Запрос информации":
        return "Спасибо. Подготавливаем ответ на ваш запрос."
    return "Спасибо за обращение. Мы свяжемся с вами."