from passlib.context import CryptContext

from core.config import login_manager, SessionLocal
from models.users import User


@login_manager.user_loader()
def get_user(email: str):
    db = SessionLocal()
    try:
        return db.query(User).filter(User.email == email).first()
    finally:
        db.close()

        
def hash_password(password: str) -> str:
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    return pwd_context.hash(password)

