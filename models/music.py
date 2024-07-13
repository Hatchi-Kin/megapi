"""models/music.py

Defines models for the music library, including SQLAlchemy models for database interactions and Pydantic models for request and response validation.

This module is part of a music management system, facilitating operations such as adding songs to the music library, querying albums, artists, and song paths.
"""

from sqlalchemy import Column, Integer, String, Float
from pydantic import BaseModel, Field

from core.config import Base

class MusicLibrary(Base):
    """
    SQLAlchemy model for the music library table.

    Attributes:
        id (Integer): The primary key, unique ID of the song.
        filename (String): The name of the file.
        filepath (String): The path to the file.
        album_folder (String): The folder name of the album.
        artist_folder (String): The folder name of the artist.
        filesize (Float): The size of the file in megabytes.
        title (String): The title of the song.
        artist (String): The artist of the song.
        album (String): The album of the song.
        year (Integer): The release year of the song.
        tracknumber (Integer): The track number of the song.
        genre (String): The genre of the song.
        top_5_genres (String): The top 5 genres of the song.
    """
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
    """
    Pydantic model for adding a song to the music library.

    Attributes mirror the MusicLibrary SQLAlchemy model, facilitating easy data transfer from request to database.
    """
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
    """
    Pydantic model for album response.

    Attributes:
        album_folder (str): The folder name of the album.
    """
    album_folder: str


class ArtistAlbumResponse(BaseModel):
    """
    Pydantic model for artist and album response.

    Attributes:
        artist (str): The artist of the album.
        album (str): The name of the album.
    """
    artist: str
    album: str


class ArtistFolderResponse(BaseModel):
    """
    Pydantic model for artist folder response.

    Attributes:
        artist_folder (str): The folder name of the artist.
    """
    artist_folder: str


class SongPath(BaseModel):
    """
    Pydantic model for song path request and response.

    Attributes:
        file_path (str): The path to the song file, with an example provided for clarity.
    """
    file_path: str = Field(..., json_schema_extra={'example': "MegaSet/No Place For Soul/2002 - Full Global Racket/04 A.I.M.mp3"})
