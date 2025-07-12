from fastapi import Depends, FastAPI
from sqlalchemy.orm import Session
from app.models.item import Item
from database import SessionLocal, engine

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/items")
def create_item(name: str, available: bool, db: Session = Depends(get_db)):
    db_item = Item(name=name, available=available)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item