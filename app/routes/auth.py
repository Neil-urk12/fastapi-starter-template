from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.token import Token
from app.repositories.user_repository import (
    authenticate,
    create,
    find_by_email,
    find_by_id,
    find_by_username,
)
from app.schemas.user import User, UserCreate
from app.services.auth_service import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    create_access_token,
    get_current_active_user,
)
from database import get_db

router = APIRouter()


@router.get("/users/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user


@router.get("/users/{user_id}", response_model=User)
async def get_user_by_id_endpoint(user_id: int, db: Session = Depends(get_db)):
    user = find_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.get("/users")
async def get_user_by_username_endpoint(username: str, db: Session = Depends(get_db)):
    user = find_by_username(db, username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.get("/users/email")
async def get_user_by_email_endpoint(email: str, db: Session = Depends(get_db)):
    user = find_by_email(db, email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.post("/users", response_model=User)
async def create_user_endpoint(user: UserCreate, db: Session = Depends(get_db)):
    # Check if user already exists
    existing_user = find_by_username(db, user.username)
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already registered")

    existing_email = find_by_email(db, user.email)
    if existing_email:
        raise HTTPException(status_code=400, detail="Email already registered")

    try:
        return create(db, user)
    except IntegrityError:
        # Lost the race: a concurrent request inserted the same username/email
        # between our pre-check and the commit. Map to 409.
        db.rollback()
        raise HTTPException(
            status_code=409, detail="Username or email already registered"
        )
    except RuntimeError as e:
        # create() raises RuntimeError only when the default role is not
        # seeded (a deployment misconfiguration, e.g. main.py skipped
        # init_db()). Map to 503 so operators see a clear signal in
        # logs/dashboards; rollback any partial transaction.
        db.rollback()
        raise HTTPException(status_code=503, detail=str(e))


@router.post('/token', response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    user = authenticate(db, form_data.username, form_data.password)
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


@router.get("/protected")
async def protected_route(current_user: User = Depends(get_current_active_user)):
    return {"message": f"Hello {current_user.username}, this is a protected route"}
