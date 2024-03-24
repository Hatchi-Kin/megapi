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
    distance: float
    entity: Entity


class SimilarEntitiesResponse(BaseModel):
    hits: List[Hit]


class EmbeddingResponse(BaseModel):
    id: str
    embedding: List[float]
