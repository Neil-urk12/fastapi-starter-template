from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from app.schemas.user import UserCreate, User
from app.models.token import Token
from app.services.auth_service import (
    authenticate_user_db, 
    create_access_token, 
    get_current_active_user,
    ACCESS_TOKEN_EXPIRE_MINUTES
)
from app.services.user_service import (
    get_user_by_id,
    get_user_by_username,
    get_user_by_email,
    create_user as create_user_service,
    convert_db_user_to_user
)
from database import get_db

router = APIRouter()

@router.get("/users/{user_id}", response_model=User)
async def get_user_by_id_endpoint(user_id: int, db: Session = Depends(get_db)):
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return convert_db_user_to_user(user)

@router.get("/users")
async def get_user_by_username_endpoint(username: str, db: Session = Depends(get_db)):
    user = get_user_by_username(db, username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return convert_db_user_to_user(user)

@router.get("/users/email")
async def get_user_by_email_endpoint(email: str, db: Session = Depends(get_db)):
    user = get_user_by_email(db, email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return convert_db_user_to_user(user)

@router.post("/users", response_model=User)
async def create_user_endpoint(user: UserCreate, db: Session = Depends(get_db)):
    # Check if user already exists
    existing_user = get_user_by_username(db, user.username)
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    existing_email = get_user_by_email(db, user.email)
    if existing_email:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    db_user = create_user_service(db, user)
    return convert_db_user_to_user(db_user)

@router.post('/token', response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = await authenticate_user_db(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/users/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user

@router.get("/protected")
async def protected_route(current_user: User = Depends(get_current_active_user)):
    return {"message": f"Hello {current_user.username}, this is a protected route"}
