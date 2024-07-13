from pydantic import BaseModel, Field
from typing import List


class S3Object(BaseModel):
    name: str
    size: int
    etag: str
    last_modified: str


class SongMetadata(BaseModel):
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
    filename: str


class UploadMP3ResponseList(BaseModel):
    uploads: List[UploadDetail]
    