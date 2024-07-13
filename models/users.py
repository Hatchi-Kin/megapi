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
    """
    Represents a user in the database, with fields for identification, authentication, and relationships to other entities.
    
    Attributes:
        __tablename__ (str): The name of the table in the database.
        id (Column): The primary key, uniquely identifying each user.
        email (Column): The user's email address, unique across the table.
        username (Column): The user's chosen username, unique across the table.
        registered_at (Column): The date and time when the user registered.
        hashed_password (Column): The user's password, stored in a hashed format for security.
        is_active (Column): A boolean indicating if the user's account is active.
        is_admin (Column): A boolean indicating if the user has administrative privileges.
        favorites (relationship): A relationship to the MusicLibrary model, representing the user's favorite music.
        uploaded_files (relationship): A relationship to the UserUploaded model, representing files uploaded by the user.
    """
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
    """
    A Pydantic model for validating user data during account creation.
    
    Attributes:
        email (str): The user's email address.
        password (str): The user's chosen password.
    """
    email: str
    password: str

class TokenData(BaseModel):
    """
    A Pydantic model for token validation, encapsulating the access token and its type.
    
    Attributes:
        access_token (str): The JWT access token.
        token_type (str): The type of the token, typically "bearer".
    """
    access_token: str
    token_type: str