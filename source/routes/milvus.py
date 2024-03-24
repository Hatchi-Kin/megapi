from fastapi import APIRouter
from fastapi import Depends
from fastapi_login.exceptions import InvalidCredentialsException
from pymilvus import connections
from pymilvus import Collection

from source.settings.config import DEFAULT_SETTINGS, manager
from source.models.embedding_512 import EmbeddingResponse, SimilarEntitiesResponse


router = APIRouter(prefix="/milvus")


@router.get("/entity/{id}", response_model=EmbeddingResponse, tags=["milvus"])
def get_entity_by_id(id: str, user=Depends(manager)):
    if not user:
        raise InvalidCredentialsException(detail="Invalid credentials")

    connections.connect(
        "default",
        uri=DEFAULT_SETTINGS.milvus_uri,
        token=DEFAULT_SETTINGS.milvus_api_key,
    )
    collection_512 = Collection(name="embeddings_512")

    entities = collection_512.query(expr=f"id in [{id}]", output_fields=["embedding"])

    # need to convert the embedding to a list of 'normal' floats instead of numpy.float32
    embedding = [float(x) for x in entities[0]["embedding"]]
    return EmbeddingResponse(id=id, embedding=embedding)


@router.get("/similar/{id}", tags=["milvus"], response_model=SimilarEntitiesResponse)
def get_similar_entities(id: str, user=Depends(manager)):
    if not user:
        raise InvalidCredentialsException(detail="Invalid credentials")

    connections.connect(
        "default",
        uri=DEFAULT_SETTINGS.milvus_uri,
        token=DEFAULT_SETTINGS.milvus_api_key,
    )
    collection_512 = Collection(name="embeddings_512")

    entities = collection_512.query(expr=f"id in [{id}]", output_fields=["embedding"])
    embedding = [float(x) for x in entities[0]["embedding"]]

    entities = collection_512.search(
        data=[embedding],
        anns_field="embedding",
        param={"nprobe": 16},
        limit=3,
        offset=1,
        output_fields=["*"],
    )

    response_list = []
    for hit in entities[0]:  # entities[0] is a Hits object
        hit_dict = {
            "id": str(hit.id),
            "distance": hit.distance,
            "entity": {
                "path": hit.entity.path,
                "title": hit.entity.title,
                "album": hit.entity.album,
                "artist": hit.entity.artist,
                "top_5_genres": ','.join(hit.entity.top_5_genres),      # convert list to string
                "embedding": ','.join(map(str, hit.entity.embedding)),  # 
            },
        }
        response_list.append(hit_dict)

    return SimilarEntitiesResponse(hits=response_list)
        




