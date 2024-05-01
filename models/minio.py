from pydantic import BaseModel, Field


class S3Object(BaseModel):
    name: str
    size: int
    etag: str
    last_modified: str


class SongMetadata(BaseModel):
    filepath: str = Field(..., example="path/to/song.mp3")
    filesize: float = Field(..., example=3.14)
    title: str = Field(..., example="Unknown Title")
    artist: str = Field(..., example="Unknown Artist")
    album: str = Field(..., example="Unknown Album")
    year: str = Field(..., example="Unknown Year")
    tracknumber: str = Field(..., example="Unknown Track Number")
    genre: str = Field(..., example="Unknown Genre")
    artwork: str = Field(None, example="base64 encoded artwork")