"""models/milvus.py

Defines Pydantic models for handling various types of responses and queries relative to milvus.

"""

from pydantic import BaseModel
from typing import List


class Entity(BaseModel):
    """
    Represents detailed information about an entity, including its path, title, album, artist, and top genres.

    Attributes:
        path (str): The file path of the entity in the bucket.
        title (str): The title of the entity.
        album (str): The album where the entity is from.
        artist (str): The artist of the entity.
        top_5_genres (str): The top 5 genres associated with the entity.
        embedding (str): The embedding vector of the entity as a string.
    """
    path: str
    title: str
    album: str
    artist: str
    top_5_genres: str
    embedding: str


class Hit(BaseModel):
    """
    Represents a search hit, including the entity's ID, title, distance score, and detailed entity information.

    Attributes:
        id (str): The unique identifier of the hit.
        title (str): The title of the hit.
        distance (float): The distance score indicating similarity.
        entity (Entity): The detailed entity information of the hit.
    """
    id: str
    title: str
    distance: float
    entity: Entity


class SimilarFullEntitiesResponse(BaseModel):
    """
    The response structure for a full similarity search, containing a list of hits.

    Attributes:
        hits (List[Hit]): A list of hits in the similarity search.
    """
    hits: List[Hit]


class SimilarShortEntity(BaseModel):
    """
    Represents a simplified entity structure for quick similarity searches, including only essential information.

    Attributes:
        title (str): The title of the entity.
        album (str): The album of the entity.
        artist (str): The artist of the entity.
        path (str): The file path of the entity.
    """
    title: str
    album: str
    artist: str
    path: str


class SimilarShortEntitiesResponse(BaseModel):
    """
    The response structure for a simplified similarity search, containing a list of simplified entities.

    Attributes:
        entities (List[SimilarShortEntity]): A list of simplified entities in the similarity search.
    """
    entities: List[SimilarShortEntity]


class EmbeddingResponse(BaseModel):
    """
    Represents the embedding response for an entity, including its unique identifier and embedding vector.

    Attributes:
        id (str): The unique identifier of the entity.
        embedding (List[float]): The embedding vector of the entity.
    """
    id: str
    embedding: List[float]


class FilePathsQuery(BaseModel):
    """
    Represents a query for file paths, typically used to fetch or validate paths in bulk operations.

    Attributes:
        path (List[str]): A list of file paths.
    """
    path: List[str]
