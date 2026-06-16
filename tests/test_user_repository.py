"""Tests for app/repositories/user_repository.py.

Locks the public contract of the repository: lookups return the User schema
(never DBUser), create() hashes passwords and assigns the default role, and
authenticate() returns None on any credential mismatch.
"""
import pytest

from app.models.user import DBUser
from app.repositories import user_repository
from app.schemas.user import User, UserCreate


def _make_user(**overrides) -> UserCreate:
    payload = {
        "username": "alice",
        "firstname": "Alice",
        "lastname": "Smith",
        "email": "alice@example.com",
        "password": "correct horse battery",
    }
    payload.update(overrides)
    return UserCreate(**payload)


# --- constants ---------------------------------------------------------------


def test_seed_roles_contains_default_role():
    """The default role assigned to new users must be seeded, otherwise
    create() silently creates role-less users."""
    assert user_repository.DEFAULT_ROLE in user_repository.SEED_ROLES


# --- create() -----------------------------------------------------------------


def test_create_returns_user_schema_with_input_fields(db_with_role):
    result = user_repository.create(db_with_role, _make_user(password="plain-text"))

    assert isinstance(result, User)
    assert result.username == "alice"
    assert result.email == "alice@example.com"
    # The schema MUST NOT expose the password back to callers.
    assert "password" not in result.model_dump()
    assert "hashed_password" not in result.model_dump()


def test_create_stores_bcrypt_hash_not_plaintext(db_with_role):
    """The stored password must be a bcrypt hash, not the plaintext."""
    db = db_with_role
    user_repository.create(db, _make_user(password="s3cret"))

    db_user = db.query(DBUser).filter(DBUser.username == "alice").one()
    assert db_user.hashed_password != "s3cret"
    # Bcrypt hashes start with $2a$, $2b$, or $2y$.
    assert db_user.hashed_password.startswith("$2")


def test_create_assigns_default_role(db_with_role):
    user_repository.create(db_with_role, _make_user())

    db_user = db_with_role.query(DBUser).filter(DBUser.username == "alice").one()
    role_names = {r.name for r in db_user.roles}
    assert user_repository.DEFAULT_ROLE in role_names


def test_create_raises_when_default_role_is_not_seeded(db):
    """A role-less user is almost certainly a deployment bug; fail loudly
    so the missing seed shows up immediately, not as a 401 in production."""
    with pytest.raises(RuntimeError, match="Default role 'user' is not seeded"):
        user_repository.create(db, _make_user())


# --- authenticate() ----------------------------------------------------------


def test_authenticate_accepts_correct_password(db_with_role):
    user_repository.create(db_with_role, _make_user(password="s3cret"))

    result = user_repository.authenticate(db_with_role, "alice", "s3cret")

    assert result is not None
    assert result.username == "alice"
    assert result.firstname == "Alice"
    assert result.lastname == "Smith"
    assert result.email == "alice@example.com"
    assert result.is_active is True


def test_authenticate_rejects_wrong_password(db_with_role):
    user_repository.create(db_with_role, _make_user(password="s3cret"))

    assert user_repository.authenticate(db_with_role, "alice", "wrong") is None


def test_authenticate_unknown_user(db):
    # No user, no role — just an empty DB.
    assert user_repository.authenticate(db, "ghost", "anything") is None


def test_authenticate_rejects_malformed_hash(db_with_role):
    """A corrupted hashed_password column must be treated as a credential
    failure, not propagated as a 500."""
    db = db_with_role
    db.add(
        DBUser(
            username="mallory",
            firstname="M",
            lastname="X",
            email="m@example.com",
            hashed_password="not-a-real-bcrypt-hash",
        )
    )
    db.commit()

    assert user_repository.authenticate(db, "mallory", "anything") is None


# --- find_by_* helpers --------------------------------------------------------


def test_find_by_username_round_trip(db_with_role):
    user_repository.create(
        db_with_role, _make_user(username="bob", email="bob@example.com")
    )

    found = user_repository.find_by_username(db_with_role, "bob")

    assert found is not None
    assert found.username == "bob"
    assert found.email == "bob@example.com"


def test_find_by_email_round_trip(db_with_role):
    user_repository.create(
        db_with_role, _make_user(username="carol", email="carol@example.com")
    )

    found = user_repository.find_by_email(db_with_role, "carol@example.com")

    assert found is not None
    assert found.email == "carol@example.com"


def test_find_by_id_round_trip(db_with_role):
    user_repository.create(
        db_with_role, _make_user(username="dave", email="dave@example.com")
    )
    # create() returns the User schema (no id), so look up the id via the model.
    user_id = (
        db_with_role.query(DBUser)
        .filter(DBUser.username == "dave")
        .one()
        .id
    )

    found = user_repository.find_by_id(db_with_role, user_id)

    assert found is not None
    assert found.username == "dave"


def test_find_helpers_return_none_when_missing(db_with_role):
    assert user_repository.find_by_username(db_with_role, "nope") is None
    assert user_repository.find_by_email(db_with_role, "nope@example.com") is None
    assert user_repository.find_by_id(db_with_role, 99999) is None
