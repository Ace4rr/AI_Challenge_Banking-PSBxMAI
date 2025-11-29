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
    extracted_data: Optional[str]
    created_at: Optional[datetime]

    class Config:
        from_attributes = True