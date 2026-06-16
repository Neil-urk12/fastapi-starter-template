"""Pytest fixtures for the test suite.

Provides an isolated in-memory SQLite session per test, plus a variant with
the default role pre-seeded (the common case for the user repository).
"""
# Provide safe defaults so the test suite runs without a `.env` file on a
# fresh checkout. In production these env vars are required and provided by
# the deployment; the defaults here never reach runtime code.
import os

os.environ.setdefault("SECRET_KEY", "test")
os.environ.setdefault("SQLALCHEMY_DATABASE_URL", "sqlite:///:memory:")

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.models.user import DBRole, DBUser
from app.repositories import user_repository


@pytest.fixture
def db() -> Session:
    """Fresh in-memory SQLite session. Tables come from DBUser.metadata
    (not database.Base) so the fixture is independent of the production
    engine. The os.environ shim at the top of this file is what lets
    `config.settings` import successfully on a fresh checkout without
    a `.env`."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    DBUser.metadata.create_all(bind=engine)
    session = sessionmaker(autocommit=False, autoflush=False, bind=engine)()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def db_with_role(db: Session) -> Session:
    """Same as `db`, but with the repository's DEFAULT_ROLE seeded."""
    db.add(DBRole(name=user_repository.DEFAULT_ROLE))
    db.commit()
    return db
