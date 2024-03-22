from sqlalchemy import Column, Integer, String, Float
from source.data.database import Base



class MusicLibrary(Base):
    __tablename__ = "music_library"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String)
    filepath = Column(String)
    album_folder = Column(String)
    artist_folder = Column(String)
    filesize = Column(Float)
    title = Column(String)
    artist = Column(String)
    album = Column(String)
    year = Column(Integer)
    tracknumber = Column(Integer)
    genre = Column(String)
    top_5_genres = Column(String)