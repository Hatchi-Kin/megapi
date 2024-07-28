from pydantic import BaseModel, validator
from typing import List, Optional


class Entity(BaseModel):
    path: str
    album: Optional[str] = 'Unknown Album'
    artist: Optional[str] = 'Unknown Artist'
    top_5_genres: List[str] = []
    embedding: List[float] = []
    title: Optional[str] = 'Unknown Title'

    @validator('top_5_genres', pre=True)
    def parse_top_5_genres(cls, value):
        if isinstance(value, str):
            return value.split(',')
        return value

    @validator('embedding', pre=True)
    def parse_embedding(cls, value):
        if isinstance(value, str):
            return [float(x) for x in value.split(',')]
        return value


class Hit(BaseModel):
    id: str
    title: str
    distance: float
    entity: Entity


class SimilarFullEntitiesResponse(BaseModel):
    hits: List[Hit]


class SimilarShortEntity(BaseModel):
    title: str
    album: str
    artist: str
    path: str


class SimilarShortEntitiesResponse(BaseModel):
    entities: List[SimilarShortEntity]


class EmbeddingResponse(BaseModel):
    id: str
    embedding: List[float]


class FilePathsQuery(BaseModel):
    path: List[str]

class SanitizedFilePathsQuery(BaseModel):
    filepath: str
