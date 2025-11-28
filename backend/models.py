# models.py
from sqlalchemy import Column, Integer, Text, DateTime
from sqlalchemy.sql import func
from .database import Base # Убедитесь, что импорт идет из .database

class Message(Base):
    __tablename__ = "messages"
    id = Column(Integer, primary_key=True, index=True)
    input_text = Column(Text, nullable=False)
    classification = Column(Text)
    generated_answer = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())