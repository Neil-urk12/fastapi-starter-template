from app.models.user import DBRole
from app.repositories.user_repository import SEED_ROLES
from database import SessionLocal


def init_db():
    """Initialize database with default roles."""
    db = SessionLocal()
    try:
        # Create default roles if they don't exist
        for role_name in SEED_ROLES:
            existing = db.query(DBRole).filter(DBRole.name == role_name).first()
            if not existing:
                db.add(DBRole(name=role_name))
        db.commit()
        print("Database initialized with default roles")
    except Exception as e:
        print(f"Error initializing database: {e}")
        db.rollback()
    finally:
        db.close()
