from app.models.user import DBRole
from database import SessionLocal

def init_db():
    """Initialize database with default roles."""
    db = SessionLocal()
    try:
        # Create default roles if they don't exist
        user_role = db.query(DBRole).filter(DBRole.name == "user").first()
        if not user_role:
            user_role = DBRole(name="user")
            db.add(user_role)

        admin_role = db.query(DBRole).filter(DBRole.name == "admin").first()
        if not admin_role:
            admin_role = DBRole(name="admin")
            db.add(admin_role)

        db.commit()
        print("Database initialized with default roles")
    except Exception as e:
        print(f"Error initializing database: {e}")
        db.rollback()
    finally:
        db.close()
