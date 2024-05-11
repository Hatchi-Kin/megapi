from sqlalchemy import Column, Integer, Table, ForeignKey

from core.config import Base


# This is the association table that creates the many-to-many relationship
favorites = Table('favorites', Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id')),
    Column('music_id', Integer, ForeignKey('music_library.id'))
)

