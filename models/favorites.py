from sqlalchemy import Column, Integer, Table, ForeignKey
from core.config import Base

# Define the 'favorites' association table for a many-to-many relationship between 'users' and 'music_library'.
# The table uses 'user_id' and 'music_id' as foreign keys to establish the relationship.
favorites = Table('favorites', Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('music_id', Integer, ForeignKey('music_library.id'), primary_key=True)
)
