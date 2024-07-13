from pydantic import BaseModel


class SongList(BaseModel):
    songs: list


class EmbeddingResponse(BaseModel):
    file_name: str
    embedding: list
