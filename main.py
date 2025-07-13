from fastapi import FastAPI
from app.routes.item import router as item_router
from app.routes.auth import router as auth_router
from app.database.init_db import init_db
from database import engine, Base

app = FastAPI(title="FastAPI Application", description="A FastAPI app with authentication and items")

# Include routers with prefixes and tags
app.include_router(item_router, prefix="/api", tags=["items"])
app.include_router(auth_router, prefix="/api", tags=["auth"])

@app.get("/")
async def index():
    return {"message": "Hello, FastAPI!", "docs": "/docs"}

@app.on_event("startup")
async def startup():
    # Create database tables
    Base.metadata.create_all(bind=engine)
    print("Connected to database and tables created")
    
    # Initialize database with default data
    init_db()

@app.on_event("shutdown")
async def shutdown():
    # Close any remaining connections
    engine.dispose()
    print("Database connections closed")

