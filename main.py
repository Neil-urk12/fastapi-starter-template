from fastapi import FastAPI
from databases import Database

app = FastAPI()
database = Database('sqlite:///test.db')

@app.get("/")
async def index():
    return {"message": "Hello, FastAPI!"}

@app.on_event("startup")
async def startup():
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

