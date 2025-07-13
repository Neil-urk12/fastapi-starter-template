from sqlalchemy.orm import Session
from passlib.context import CryptContext
from app.models.user import DBUser, DBRole
from app.schemas.user import UserCreate, User
from typing import Optional

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_user_by_id(db: Session, user_id: int) -> Optional[DBUser]:
    """Get a user by ID."""
    return db.query(DBUser).filter(DBUser.id == user_id).first()

def get_user_by_username(db: Session, username: str) -> Optional[DBUser]:
    """Get a user by username."""
    return db.query(DBUser).filter(DBUser.username == username).first()

def get_user_by_email(db: Session, email: str) -> Optional[DBUser]:
    """Get a user by email."""
    return db.query(DBUser).filter(DBUser.email == email).first()

def create_user(db: Session, user: UserCreate) -> DBUser:
    """Create a new user."""
    hashed_password = pwd_context.hash(user.password)
    db_user = DBUser(
        username=user.username,
        firstname=user.firstname,
        lastname=user.lastname,
        email=user.email,
        hashed_password=hashed_password
    )
    
    # Assign default user role
    user_role = db.query(DBRole).filter(DBRole.name == "user").first()
    if user_role:
        db_user.roles.append(user_role)
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def convert_db_user_to_user(db_user: DBUser) -> User:
    """Convert DBUser to User model."""
    return User(
        username=db_user.username,
        firstname=db_user.firstname,
        lastname=db_user.lastname,
        email=db_user.email,
        disabled=not db_user.is_active
    )