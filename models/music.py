from sqlalchemy import Column, Integer, String, Float
from pydantic import BaseModel, Field

from core.config import Base


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


class AddSongToMusicLibrary(BaseModel):
    filename: str
    filepath: str
    album_folder: str
    artist_folder: str
    filesize: float
    title: str
    artist: str
    album: str
    year: int
    tracknumber: int
    genre: str
    top_5_genres: str


class AlbumResponse(BaseModel):
    album_folder: str


class ArtistAlbumResponse(BaseModel):
    artist: str
    album: str


class ArtistFolderResponse(BaseModel):
    artist_folder: str


class SongPath(BaseModel):
    file_path: str = Field(..., example="MegaSet/No Place For Soul/2002 - Full Global Racket/04 A.I.M.mp3")

