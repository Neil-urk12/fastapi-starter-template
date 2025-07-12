from pydantic import BaseModel
from typing import Optional

class Item(BaseModel):
    id: int
    name: str
    available: bool

class ItemUpdate(BaseModel):
    name: Optional[str] = None
    available: Optional[bool] = None

class ItemPost(BaseModel):
    name: str
    available: bool