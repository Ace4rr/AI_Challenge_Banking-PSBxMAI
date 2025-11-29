from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class MessageCreate(BaseModel):
    text: str
    sla: Optional[str] = None
    tone: Optional[str] = None


class MessageOut(BaseModel):
    id: int
    input_text: str
    classification: Optional[str]
    generated_answer: Optional[str]
    created_at: Optional[datetime]

    class Config:
        orm_mode = True

class UserCreate(BaseModel):
    username:str
    email: str
    password: str 
    role: str="client"

class UserOut(BaseModel):
    id: int 
    username: str 
    email: str
    role:str

    class Config:
        orm_mode=True

