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
    created_at: Optional[datetime]

    class Config:
        orm_mode = True
        
class UserCreate(BaseModel):
    username:str
    email: str
    password: str 

class UserOut(BaseModel):
    id: int 
    username: int 
    email: str

    class Config:
        orm_mode=True

