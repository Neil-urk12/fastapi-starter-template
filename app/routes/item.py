from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models.item import Item
from app.schemas.item import ItemUpdate
from database import get_db

router = APIRouter()

@router.post("/items")
async def create_item(name: str, available: bool, db: Session = Depends(get_db)):
    db_item = Item(name=name, available=available)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

@router.get("/items")
async def get_items(db: Session = Depends(get_db)):
    items = db.query(Item).all()
    return items

@router.get("/items/{item_id}")
async def get_item(item_id: int, db: Session = Depends(get_db)):
    item = db.query(Item).filter(Item.id == item_id).first()
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return item

@router.patch("/items/{item_id}")
async def update_item(item_id: int, item_update: ItemUpdate, db: Session = Depends(get_db)):
    db_item = db.query(Item).filter(Item.id == item_id).first()
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")

    update_data = item_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_item, key, value)

    db.commit()
    db.refresh(db_item)
    return db_item