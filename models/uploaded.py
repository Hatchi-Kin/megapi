"""models.uploaded.py

This module defines the SQLAlchemy model for user-uploaded files.

It establishes the structure and relationships of the `user_uploads` table in the database, which stores information about files uploaded by users. Each record in this table is linked to a specific user, enabling tracking of who uploaded what file.
"""

from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from core.config import Base  # Base is assumed to be the declarative base class for SQLAlchemy models.


class UserUploaded(Base):
    """
    Represents an uploaded file by a user in the database.
    
    Attributes:
        __tablename__ (str): The name of the table in the database.
        id (Column): The primary key of the table, uniquely identifying each uploaded file.
        filename (Column): The name of the uploaded file. Indexed for faster queries.
        user_id (Column): A foreign key linking to the 'id' column in the 'users' table.
        user (relationship): A SQLAlchemy ORM relationship that links each uploaded file to a specific user.
    """
    __tablename__ = "user_uploads"
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship("User", back_populates="uploaded_files")
