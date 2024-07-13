from passlib.context import CryptContext
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from datetime import timedelta

from core.config import login_manager, SessionLocal, DEFAULT_SETTINGS
from models.users import User


class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        authorization: str = request.headers.get('Authorization')
        if authorization:
            try:
                token = authorization.split(' ')[1]
                user = await login_manager.get_current_user(token)
                if user:
                    access_token_expires = timedelta(minutes=DEFAULT_SETTINGS.access_token_expire_minutes)
                    new_token = login_manager.create_access_token(
                        data=dict(sub=user.email), expires=access_token_expires
                    )
                    response = await call_next(request)
                    response.headers['Authorization'] = f'Bearer {new_token}'
                    return response
            except:
                pass
        return await call_next(request)
    
    
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
