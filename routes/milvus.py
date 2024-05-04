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
    convert_plot_to_base64
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
    
    # Get the predictions, title, and artist from the queried entity
    embeddings = entity[0]["predictions"]
    title = entity[0]["title"]
    artist = entity[0]["artist"]

    # Open and load the JSON file containing list of classes the model can predict
    with open('utils/mtg_jamendo_genre.json', 'r') as json_file:
        metadata = json.load(json_file)

    # Get the list of classes from the metadata
    classes = metadata.get('classes')

    # Convert the list of predictions to a NumPy array
    embeddings = np.array(embeddings)

    # Check the shape of embeddings
    print(embeddings.shape)

    # If embeddings is not a 2D array, reshape it
    if len(embeddings.shape) == 1:
        embeddings = embeddings.reshape(1, -1)

    # Calculate average activations for each class
    average_activations = np.mean(embeddings, axis=0)

    # Convert the average activations to float32
    average_activations_float = average_activations.astype(np.float32)

    # Get sorted indices based on average activations
    sorted_indices = np.argsort(average_activations_float)

    # Get top 5 classes
    top_5_classes = sorted_indices[-5:]

    # Get corresponding average activations
    top_5_activations = average_activations_float[top_5_classes]

    # Get class names
    class_names = np.array(metadata['classes'])[top_5_classes]

    # Create bar plot
    fig, ax = plt.subplots(figsize=(6, 2))
    plt.barh(class_names, top_5_activations, color='#60a5fa', edgecolor='#cbd5e1')
    plt.title(f'Genres for {title} by {artist}', color='#cbd5e1')
    plt.tick_params(colors='#cbd5e1')

    # Set plot background color
    ax.set_facecolor('#111827')
    fig.patch.set_facecolor('#111827')

    # Convert plot to base64
    buf = io.BytesIO()
    fig.savefig(buf, format='png')
    buf.seek(0)
    image_base64 = base64.b64encode(buf.read()).decode('utf-8')

    return Response(content=image_base64, media_type="text/plain")