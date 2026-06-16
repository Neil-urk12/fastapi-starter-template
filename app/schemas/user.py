from typing import Optional

from pydantic import BaseModel


class User(BaseModel):
    username: str
    firstname: str
    lastname: str
    email: Optional[str] = None
    is_active: bool


class UserCreate(BaseModel):
    username: str
    firstname: str
    lastname: str
    email: str
    password: str
