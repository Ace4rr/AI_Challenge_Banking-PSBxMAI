from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class MessageCreate(BaseModel):
    text: str

class MessageOut(BaseModel):
    id: int
    input_text: str
    classification: Optional[str]
    generated_answer: Optional[str]
    extracted_data: Optional[str] # НОВОЕ ПОЛЕ
    created_at: Optional[datetime]

    class Config:
        from_attributes = True # В Pydantic v2 orm_mode переименован в from_attributes