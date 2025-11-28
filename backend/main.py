from fastapi import FastAPI

app = FastAPI(
    title="IceCoffee Project",
    description="Test file main.py",
    version="1.0.0"
)

@app.get("/")
async def root():
    return {"message": "Hello World!"}

@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello, {name}!"}

@app.post("/message")
async def create_message(message: str):
    return {"received_message": message, "status": "Message received successfully"}