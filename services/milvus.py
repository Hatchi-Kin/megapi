from pymilvus import connections
from pymilvus import Collection

from core.config import DEFAULT_SETTINGS


def get_milvus_collection():
    connections.connect(
        "default",
        uri=DEFAULT_SETTINGS.milvus_uri,
        token=DEFAULT_SETTINGS.milvus_api_key,
    )
    return Collection(name=DEFAULT_SETTINGS.milvus_collection_name)


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
        "path": hit.entity.path,
    }


def sort_entities(entities):
    # try to filter out already recommended artists
    recommended_artists = set()
    response_list = []
    fallback_list = []
    for hit in entities[0]:
        hit_dict = short_hit_to_dict(hit)
        if hit_dict["artist"] not in recommended_artists:
            response_list.append(hit_dict)
            recommended_artists.add(hit_dict["artist"])
        else:
            fallback_list.append(hit_dict)
        if len(response_list) == 9:  # Stop when we have 9 results
            break
    # If we have less than 9 results, add from fallback_list
    if len(response_list) < 9:
        response_list.extend(fallback_list[:9-len(response_list)])

    return response_list