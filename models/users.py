from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship
from pydantic import BaseModel

from core.config import Base
from models.favorites import favorites


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    registered_at = Column(String)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)

    # Relationship field
    favorites = relationship("MusicLibrary", secondary=favorites, backref="users")


class UserCreate(BaseModel):
    email: str
    password: str


class TokenData(BaseModel):
    access_token: str
    token_type: str