import os
from datetime import timedelta

from fastapi import Depends, HTTPException
from fastapi.responses import HTMLResponse
from fastapi_login.exceptions import InvalidCredentialsException
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import bcrypt

from models.users import User, UserCreate, TokenData
from services.auth import get_user, hash_password
from core.config import login_manager, DEFAULT_SETTINGS
from core.database import get_db


router = APIRouter(prefix="/auth")


@router.get("/users/me", tags=["users"])
async def read_users_me(user: User = Depends(login_manager)):
    return user


@router.post("/register", tags=["users"])
def register(user: UserCreate, db: Session = Depends(get_db)):
    """Register a new user."""
    db_user = get_user(user.email)
    if db_user:
        raise HTTPException(
            status_code=400, detail="A user with this email already exists"
        )
    hashed_password = hash_password(user.password)
    db_user = User(email=user.email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    return {"detail": "Successful registered"}


@router.get("/gui", tags=["auth gui"])
def index():
    """Render a front-end to test signup/login page."""
    file_path = os.path.join("gui", "templates", "index.html")
    with open(file_path, "r") as f:
        return HTMLResponse(content=f.read())


@router.post("/token", tags=["users"], response_model=TokenData)
def login(data: OAuth2PasswordRequestForm = Depends()):
    """Authenticate a user and return an access token."""
    email = data.username
    password = data.password
    user = get_user(email)
    if not user or not bcrypt.checkpw(
        password.encode("utf-8"), user['hashed_password'].encode("utf-8")
    ):
        raise InvalidCredentialsException
    access_token_expires = timedelta(minutes=DEFAULT_SETTINGS.access_token_expire_minutes)
    access_token = login_manager.create_access_token(
        data=dict(sub=email), expires=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.delete("/users/{user_id}", tags=["users"])
def delete_user(
    user_id: int, current_user=Depends(login_manager), db: Session = Depends(get_db)
):
    """Delete a user."""
    if not current_user:
        raise InvalidCredentialsException(detail="Invalid credentials")
    if current_user.id != 1:
        raise HTTPException(status_code=401, detail="Unauthorized")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()
    return {"detail": "User deleted"} @ router.get(
        "/private",
        tags=["users"],
        summary="A private route that requires authentication.",
    )


@router.get("/private", tags=["users"], summary="A private route that requires authentication.")
def private_route(user=Depends(login_manager)):
    """A private route that requires authentication."""
    return {"detail": f"Welcome {user.email}, you are authenticated"}


@router.get("/users", tags=["users"])
def list_users(user=Depends(login_manager), db: Session = Depends(get_db)):
    """List all users."""
    users = db.query(User).all()
    users = [{"id": user.id, "email": user.email} for user in users]
    return users
