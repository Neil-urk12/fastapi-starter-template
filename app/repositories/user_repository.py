"""User persistence: lookups, creation, password hashing, credential check.

This module owns the User concept end-to-end: it is the only place in the
application that knows how a user is stored or verified. Routes and the
FastAPI auth dependency cross this seam; SQLAlchemy does not leak past it.
"""
from typing import Optional

from passlib.context import CryptContext
from passlib.exc import UnknownHashError
from sqlalchemy.orm import Session

from app.models.user import DBRole, DBUser
from app.schemas.user import User, UserCreate

# Canonical role names. Single source of truth for both seeding and the
# default role assigned on user creation.
SEED_ROLES: tuple[str, ...] = ("user", "admin")
DEFAULT_ROLE: str = "user"

# Password hashing. Private to this module.
_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def _to_schema(db_user: DBUser) -> User:
    """Translate DBUser -> User. The only place that knows about the
    DBUser.is_active -> User.is_active mapping."""
    return User(
        username=db_user.username,
        firstname=db_user.firstname,
        lastname=db_user.lastname,
        email=db_user.email,
        is_active=db_user.is_active,
    )


def find_by_id(db: Session, user_id: int) -> Optional[User]:
    db_user = db.query(DBUser).filter(DBUser.id == user_id).first()
    return _to_schema(db_user) if db_user else None


def find_by_email(db: Session, email: str) -> Optional[User]:
    db_user = db.query(DBUser).filter(DBUser.email == email).first()
    return _to_schema(db_user) if db_user else None


def find_by_username(db: Session, username: str) -> Optional[User]:
    db_user = db.query(DBUser).filter(DBUser.username == username).first()
    return _to_schema(db_user) if db_user else None


def create(db: Session, user: UserCreate) -> User:
    """Create a new user. Hashes the password internally and assigns the
    default role."""
    db_user = DBUser(
        username=user.username,
        firstname=user.firstname,
        lastname=user.lastname,
        email=user.email,
        hashed_password=_pwd_context.hash(user.password),
    )
    user_role = db.query(DBRole).filter(DBRole.name == DEFAULT_ROLE).first()
    if user_role is None:
        raise RuntimeError(
            f"Default role '{DEFAULT_ROLE}' is not seeded. Call init_db() first."
        )
    db_user.roles.append(user_role)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return _to_schema(db_user)


def authenticate(db: Session, username: str, plain_password: str) -> Optional[User]:
    """Verify a username + password against the database. Returns the User
    on success, None on failure."""
    db_user = db.query(DBUser).filter(DBUser.username == username).first()
    if db_user is None:
        return None
    try:
        ok = _pwd_context.verify(plain_password, db_user.hashed_password)
    except UnknownHashError:
        return None
    if not ok:
        return None
    return _to_schema(db_user)
