from fastapi import Depends, HTTPException
from fastapi.responses import HTMLResponse
from fastapi_login.exceptions import InvalidCredentialsException
from fastapi.security import OAuth2PasswordRequestForm
import bcrypt
from fastapi import APIRouter, Depends
from source.models.users import User, UserCreate
from source.dependencies.config import manager, get_user, SessionLocal


router = APIRouter(prefix="/auth")

@manager.user_loader()
def get_user(email: str):
    db = SessionLocal()
    try:
        return db.query(User).filter(User.email == email).first()
    finally:
        db.close()

@router.post("/register", tags=["users"])
def register(user: UserCreate):
    db = SessionLocal()
    try:
        db_user = db.query(User).filter(User.email == user.email).first()
        if db_user:
            raise HTTPException(
                status_code=400, detail="A user with this email already exists"
            )
        else:
            hashed_password = bcrypt.hashpw(
                user.password.encode("utf-8"), bcrypt.gensalt()
            ).decode("utf-8")
            db_user = User(email=user.email, hashed_password=hashed_password)
            db.add(db_user)
            db.commit()
            return {"detail": "Successful registered"}
    finally:
        db.close()


@router.post("/token", tags=["users"])
def login(data: OAuth2PasswordRequestForm = Depends()):
    email = data.username
    password = data.password

    user = get_user(email)
    if not user:
        raise InvalidCredentialsException
    elif not bcrypt.checkpw(
        password.encode("utf-8"), user.hashed_password.encode("utf-8")
    ):
        raise InvalidCredentialsException

    access_token = manager.create_access_token(data=dict(sub=email))
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/private", tags=["users"])
def private_route(user=Depends(manager)):
    if not user:
        raise InvalidCredentialsException(detail="Invalid credentials")
    return {"detail": f"Welcome {user.email}"}


@router.get("/gui", tags=["signup / login"])
def index():
    with open("source/templates/index.html", "r") as f:
        return HTMLResponse(content=f.read())
