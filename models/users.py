"""models/users.py

The User model represents the structure of the 'users' table in the database, including fields for user identification, authentication, and relationships to other entities like uploaded files and favorites.

The UserCreate model is a Pydantic model used for validating user data during account creation, ensuring that necessary fields like email and password are provided and correctly formatted.

The TokenData model is another Pydantic model designed for token validation, encapsulating the access token and its type, typically used in authentication processes.
"""

from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship
from pydantic import BaseModel

from core.config import Base
from models.favorites import favorites
from models.uploaded import UserUploaded

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    registered_at = Column(String)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)

    favorites = relationship("MusicLibrary", secondary=favorites, backref="users")
    uploaded_files = relationship("UserUploaded", order_by=UserUploaded.id, back_populates="user")

class UserCreate(BaseModel):
    email: str
    password: str

class TokenData(BaseModel):
    access_token: str
    token_type: str