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
    distance: float
    entity: Entity

class SimilarEntitiesResponse(BaseModel):
    hits: List[Hit]


###### similar_9_by_path  ######
class Similar_9_Entity(BaseModel):
    title: str
    album: str
    artist: str

class Similar_9_EntitiesResponse(BaseModel):
    entities: List[Similar_9_Entity]


###### similar_9_by_path  ######
class EmbeddingResponse(BaseModel):
    id: str
    embedding: List[float]

###### entity/{id} ######
class FilePathsQuery(BaseModel):
    paths: list
