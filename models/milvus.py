from pydantic import BaseModel
from typing import List


class Entity(BaseModel):
    path: str
    title: str
    album: str
    artist: str
    top_5_genres: str
    embedding: str


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
