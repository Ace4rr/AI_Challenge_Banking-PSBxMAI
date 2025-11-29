# backend/schemas.py (пример)

from pydantic import BaseModel
from datetime import datetime

# Класс для создания сообщения (без изменений)
class MessageCreate(BaseModel):
    text: str

# Класс для вывода сообщения (ОБНОВЛЕН)
class MessageOut(BaseModel):
    id: int
    input_text: str
    
    # Обновленные/Переименованные поля
    category: str
    official_reply: str
    parameters: str
    
    # НОВЫЕ ПОЛЯ
    reply_style: str
    time_to_reply: str
    summary: str
    infrastructure_sphere: str
    risks_and_fixes: str
    
    created_at: datetime

    class Config:
        from_attributes = True # Или orm_mode = True в старых версиях Pydantic