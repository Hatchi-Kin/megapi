import json

from fastapi import APIRouter, HTTPException, Depends, Response

from core.config import login_manager
from models.milvus import EmbeddingResponse, SimilarFullEntitiesResponse, FilePathsQuery, SimilarShortEntitiesResponse
from models.music import SongPath
from services.milvus import (
    get_milvus_512_collection,
    get_milvus_87_collection,
    full_hit_to_dict,
    short_hit_to_dict,
    sort_entities,
    extract_plot_data,
    create_plot,
    convert_plot_to_base64,
    ping_milvus,
)
import io
import base64
import numpy as np
import matplotlib.pyplot as plt


router = APIRouter(prefix="/milvus")


@router.get("/entity/{id}", response_model=EmbeddingResponse, tags=["milvus"])
def get_entity_by_id(id: str, user=Depends(login_manager)):
    """Get the embedding of an entity by it's id."""
    collection_512 = get_milvus_512_collection()
    entities = collection_512.query(expr=f"id in [{id}]", output_fields=["embedding"])
    if not entities:
        raise HTTPException(status_code=404, detail="Entity not found")
    
    embedding = [float(x) for x in entities[0]["embedding"]]
    return EmbeddingResponse(id=id, embedding=embedding)


@router.get("/similar/{id}", tags=["milvus"], response_model=SimilarFullEntitiesResponse)
def get_similar_entities(id: str, user=Depends(login_manager)):
    """Get the most 3 similar entities to the entity with the given id."""
    collection_512 = get_milvus_512_collection()
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
    collection_512 = get_milvus_512_collection()
    entities = collection_512.query(expr=f"path in {query.path}", output_fields=["embedding"])
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
    collection_512 = get_milvus_512_collection()
    entities = collection_512.query(expr=f"path in {query.path}", output_fields=["embedding"])
    if not entities:
        raise HTTPException(status_code=404, detail="Entity not found")
    
    embeddings = [[float(x) for x in entity["embedding"]] for entity in entities]
    entities = collection_512.search(
        data=embeddings,
        anns_field="embedding",
        param={"nprobe": 16},
        limit=30,
        offset=1,
        output_fields=["title", "album", "artist", "path"],
    )
    
    sorted_entities = sort_entities(entities)
    return {"entities": sorted_entities}


@router.post("/plot_genres", tags=["milvus"])
async def get_genres_plot(query: SongPath, user=Depends(login_manager)):
    """Get a plot of the top 5 genres of the entity with the given file path."""
    collection_87 = get_milvus_87_collection()
    entity = collection_87.query(
        expr=f"path == '{query.file_path}'",
        output_fields=["predictions", "title", "artist"], 
        limit=1
    )
    if not entity:
        raise HTTPException(status_code=404, detail="Entity not found")
    
    class_names, top_5_activations, title, artist = await extract_plot_data(entity)
    fig = await create_plot(class_names, top_5_activations, title, artist)
    image_base64 = await convert_plot_to_base64(fig)

    return Response(content=image_base64, media_type="text/plain")


@router.post("/ping", tags=["milvus"])
def ping_milvus():
    """Check if Milvus is up and running."""
    milvus_status = ping_milvus()
    return milvus_status