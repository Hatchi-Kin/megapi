from passlib.context import CryptContext

from core.config import login_manager, SessionLocal
from models.users import User


@login_manager.user_loader()
def get_user(email: str):
    """
    Retrieves a user from the database by their email address.
    
    This function is decorated with @login_manager.user_loader, indicating it's used by Flask-Login to load a user from a session.
    It queries the database for a user with the given email and returns the user object if found.
    
    Args:
        email (str): The email address of the user to retrieve.
        
    Returns:
        User: The user object if found, otherwise None.
    """
    db = SessionLocal()
    try:
        return db.query(User).filter(User.email == email).first()
    finally:
        db.close()


def hash_password(password: str) -> str:
    """
    Hashes a password using the bcrypt algorithm.
    
    This function uses Passlib's CryptContext for secure password hashing. The 'bcrypt' scheme is specified, with 'deprecated' set to 'auto' to automatically handle deprecated hash formats.
    
    Args:
        password (str): The plaintext password to hash.
        
    Returns:
        str: The hashed password.
    """
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    return pwd_context.hash(password)
