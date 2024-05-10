from pydantic import BaseModel
from typing import List


######  similar_by_path ######
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


###### similar_9_by_path  ######
class SimilarShortEntity(BaseModel):
    title: str
    album: str
    artist: str
    path: str

class SimilarShortEntitiesResponse(BaseModel):
    entities: List[SimilarShortEntity]


###### similar_9_by_path  ######
class EmbeddingResponse(BaseModel):
    id: str
    embedding: List[float]

###### entity/{id} ######
class FilePathsQuery(BaseModel):
    path: list
