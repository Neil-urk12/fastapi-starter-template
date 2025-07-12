from fastapi import FastAPI
from app.routes.item import router as item_router
from database import engine, Base

app = FastAPI()

app.include_router(item_router)

@app.get("/")
async def index():
    return {"message": "Hello, FastAPI!"}

@app.on_event("startup")
async def startup():
    # Create database tables
    Base.metadata.create_all(bind=engine)
    print("Connected to database and tables created")

@app.on_event("shutdown")
async def shutdown():
    # Close any remaining connections
    engine.dispose()
    print("Database connections closed")

