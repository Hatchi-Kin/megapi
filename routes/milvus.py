from fastapi import APIRouter, HTTPException
from fastapi import Depends
from pymilvus import connections
from pymilvus import Collection

from core.config import DEFAULT_SETTINGS, login_manager
from models.milvus import EmbeddingResponse, SimilarFullEntitiesResponse, FilePathsQuery, SimilarShortEntitiesResponse


router = APIRouter(prefix="/milvus")


def get_milvus_collection():
    connections.connect(
        "default",
        uri=DEFAULT_SETTINGS.milvus_uri,
        token=DEFAULT_SETTINGS.milvus_api_key,
    )
    return Collection(name="embeddings_512")


def full_hit_to_dict(hit):
    return {
        "id": str(hit.id),
        "distance": hit.distance,
        "entity": {
            "path": hit.entity.path,
            "title": hit.entity.title,
            "album": hit.entity.album,
            "artist": hit.entity.artist,
            "top_5_genres": ",".join(hit.entity.top_5_genres),
            "embedding": ",".join(map(str, hit.entity.embedding)),
        },
    }

def short_hit_to_dict(hit):
    return {
        "title": hit.entity.title,
        "album": hit.entity.album,
        "artist": hit.entity.artist,
    }


@router.get("/entity/{id}", response_model=EmbeddingResponse, tags=["milvus"])
def get_entity_by_id(id: str, user=Depends(login_manager)):
    """Get the embedding of an entity by it's id."""
    collection_512 = get_milvus_collection()
    entities = collection_512.query(expr=f"id in [{id}]", output_fields=["embedding"])
    if not entities:
        raise HTTPException(status_code=404, detail="Entity not found")
    
    embedding = [float(x) for x in entities[0]["embedding"]]
    return EmbeddingResponse(id=id, embedding=embedding)


@router.get("/similar/{id}", tags=["milvus"], response_model=SimilarFullEntitiesResponse)
def get_similar_entities(id: str, user=Depends(login_manager)):
    """Get the most 3 similar entities to the entity with the given id."""
    collection_512 = get_milvus_collection()
    entities = collection_512.query(expr=f"id in [{id}]", output_fields=["embedding"])
    if not entities:
        raise HTTPException(status_code=404, detail="Entity not found")

    embedding = [float(x) for x in entities[0]["embedding"]]
    entities = collection_512.search(
        data=[embedding],
        anns_field="embedding",
        param={"nprobe": 16},
        limit=3,
        offset=1,
        output_fields=["*"],
    )

    response_list = [full_hit_to_dict(hit) for hit in entities[0]]
    return SimilarFullEntitiesResponse(hits=response_list)


@router.post("/similar_full_entity", tags=["milvus"], response_model=SimilarFullEntitiesResponse)
def get_similar_entities_by_path(query: FilePathsQuery, user=Depends(login_manager)):
    """Get the most 3 similar entities (with embeddings_512) to the entity with the given file path."""
    collection_512 = get_milvus_collection()
    entities = collection_512.query(expr=f"path in {query.paths}", output_fields=["embedding"])
    if not entities:
        raise HTTPException(status_code=404, detail="Entity not found")
    
    embeddings = [[float(x) for x in entity["embedding"]] for entity in entities]
    entities = collection_512.search(
        data=embeddings,
        anns_field="embedding",
        param={"nprobe": 16},
        limit=3,
        offset=1,
        output_fields=["*"],
    )

    response_list = [short_hit_to_dict(hit) for hit in entities[0]]
    return SimilarFullEntitiesResponse(hits=response_list)


@router.post("/similar_short_entity", tags=["milvus"], response_model=SimilarShortEntitiesResponse)
def get_similar_9_entities_by_path(query: FilePathsQuery, user=Depends(login_manager)):
    """Get the 9 most similar (title, artist, album)) to the entity with the given file path."""
    collection_512 = get_milvus_collection()
    entities = collection_512.query(expr=f"path in {query.paths}", output_fields=["embedding"])
    if not entities:
        raise HTTPException(status_code=404, detail="Entity not found")
    
    embeddings = [[float(x) for x in entity["embedding"]] for entity in entities]
    entities = collection_512.search(
        data=embeddings,
        anns_field="embedding",
        param={"nprobe": 16},
        limit=9,
        offset=1,
        output_fields=["title", "album", "artist", "path"],
    )

    response_list = [short_hit_to_dict(hit) for hit in entities[0]]
    return {"entities": response_list}