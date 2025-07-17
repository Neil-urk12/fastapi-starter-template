import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from app.schemas.user import User
from app.models.user import DBUser
from app.models.token import TokenData
from database import get_db
from config import settings

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create a JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_password(plain_password, hashed_password):
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    """Generate a hash for a password."""
    return pwd_context.hash(password)

def get_user_by_email(db: Session, email: str):
    """Get a user from the database by email."""
    return db.query(DBUser).filter(DBUser.email == email).first()

def get_user_by_username(db: Session, username: str):
    """Get a user from the database by username."""
    return db.query(DBUser).filter(DBUser.username == username).first()

async def authenticate_user_db(username: str, password: str, db: Session):
    """Authenticate user against the database."""
    user = get_user_by_username(db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """Get the current user from the JWT token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except JWTError:
        raise credentials_exception

    user = get_user_by_email(db, email=token_data.email)
    if user is None:
        raise credentials_exception
    return User(
        username=user.username,
        firstname=user.firstname,
        lastname=user.lastname,
        email=user.email,
        disabled=not user.is_active
    )


async def get_current_active_user(current_user: User = Depends(get_current_user)):
    """Get the current active user (not disabled)."""
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user
