from fastapi import FastAPI, Depends
from contextlib import asynccontextmanager 
from .database import get_db, create_db_and_tables 
from . import crud, ai, schemas
from sqlalchemy.ext.asyncio import AsyncSession


@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_db_and_tables() 
    print("Database and tables created successfully!")
    
    yield
    
    print("Application shutting down...")

app = FastAPI(lifespan=lifespan) 


@app.post("/analyze")
async def analyze(payload: schemas.MessageCreate,user_id:int, db: AsyncSession = Depends(get_db)):
    text = payload.text
    classification = ai.classify_text(text)
    answer = ai.generate_answer(classification, text)

    msg = await crud.create_message(db, user_id, text, classification, answer)
    return msg

@app.post("/register",response_model=schemas.UserOut)
async def register(user: schemas.UserCreate, db: AsyncSession=Depends(get_db)):
    existing = await crud.get_user_by_username(db,user.username)
    if existing:
        return{"error":"User already exists"}
    new_user=await crud.create_user(db,user.username,user.email,user.password,user.role)
    return new_user

@app.post("/login")
async def login(user: schemas.UserCreate,db:AsyncSession=Depends(get_db)):
    auth_user=await crud.authenticate_user(db,user.username,user.password)
    if not auth_user:   
        return{"error":"Invalid username or password"}
    return {"message":"Login succesful","user_id":auth_user.id}

@app.get("/messages")
async def list_messages(db: AsyncSession = Depends(get_db)):
    return await crud.get_messages(db)

@app.get("/messages/{user_id}")
async def user_messages(user_id: int, db: AsyncSession = Depends(get_db)):
    return await crud.get_messages_by_user(db, user_id)