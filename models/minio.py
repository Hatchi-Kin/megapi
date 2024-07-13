"""models/minio.py

Defines models for handling S3 objects and song metadata, including the structure for upload responses.

This module is used for defining the data structures that interact with MinIO (or any S3 compatible storage),
handling song metadata extraction, and formatting the response for MP3 uploads.
"""

from pydantic import BaseModel, Field
from typing import List


class S3Object(BaseModel):
    """
    Represents an object stored in S3.

    Attributes:
        name (str): The name of the object.
        size (int): The size of the object in bytes.
        etag (str): The ETag of the object.
        last_modified (str): The last modified timestamp of the object.
    """
    name: str
    size: int
    etag: str
    last_modified: str


class SongMetadata(BaseModel):
    """
    Represents the metadata of a song.

    Attributes:
        filepath (str): The file path of the song within the storage system.
        filesize (float): The size of the song file in megabytes.
        title (str): The title of the song.
        artist (str): The artist of the song.
        album (str): The album where the song is from.
        year (str): The release year of the song.
        tracknumber (str): The track number of the song within the album.
        genre (str): The genre of the song.
        artwork (str, optional): The base64 encoded artwork of the song, if available.
    """
    filepath: str = Field(..., json_schema_extra={'example':"MegaSet/No Place For Soul/2002 - Full Global Racket/04 A.I.M.mp3"})
    filesize: float = Field(..., json_schema_extra={'example': 3.14})
    title: str = Field(..., json_schema_extra={'example': "Track Title"})
    artist: str = Field(..., json_schema_extra={'example': "Track Artist"})
    album: str = Field(..., json_schema_extra={'example': "Track Album"})
    year: str = Field(..., json_schema_extra={'example': "Track Year"})
    tracknumber: str = Field(..., json_schema_extra={'example': "Track Track Number"})
    genre: str = Field(..., json_schema_extra={'example': "Track Genre"})  # Corrected typo from "Traack Genre" to "Track Genre"
    artwork: str = Field(None, json_schema_extra={'example': "base64 encoded artwork"})


class UploadDetail(BaseModel):
    """
    Represents the detail of an uploaded file.

    Attributes:
        filename (str): The name of the uploaded file.
    """
    filename: str


class UploadMP3ResponseList(BaseModel):
    """
    Represents the response structure for a list of uploaded MP3 files.

    Attributes:
        uploads (List[UploadDetail]): A list of details for each uploaded file.
    """
    uploads: List[UploadDetail]
    