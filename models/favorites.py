"""models/favorites.py

Provides the definition of the 'favorites' table used to establish a many-to-many relationship between users and music tracks in the database. It utilizes SQLAlchemy for ORM functionality.

Attributes:
    favorites (Table): A SQLAlchemy Table object representing the 'favorites' association table. It links 'users' and 'music_library' tables.
"""

from sqlalchemy import Column, Integer, Table, ForeignKey
from core.config import Base

# Define the 'favorites' association table for a many-to-many relationship between 'users' and 'music_library'.
# The table uses 'user_id' and 'music_id' as foreign keys to establish the relationship.
favorites = Table('favorites', Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('music_id', Integer, ForeignKey('music_library.id'), primary_key=True)
)
