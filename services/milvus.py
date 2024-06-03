import io
import base64
from typing import List
import json

import numpy as np
import matplotlib.pyplot as plt
from pymilvus import connections
from pymilvus import Collection

from core.config import DEFAULT_SETTINGS


def ping_milvus():
    connections.connect(
        "default",
        uri=DEFAULT_SETTINGS.milvus_uri,
        token=DEFAULT_SETTINGS.milvus_api_key,
    )
    status = connections.get_connection("default").client().status()
    return status


def get_milvus_512_collection():
    connections.connect(
        "default",
        uri=DEFAULT_SETTINGS.milvus_uri,
        token=DEFAULT_SETTINGS.milvus_api_key,
    )
    return Collection(name=DEFAULT_SETTINGS.milvus_512_collection_name)


def get_milvus_87_collection():
    connections.connect(
        "default",
        uri=DEFAULT_SETTINGS.milvus_uri,
        token=DEFAULT_SETTINGS.milvus_api_key,
    )
    return Collection(name=DEFAULT_SETTINGS.milvus_87_collection_name)


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


async def extract_plot_data(entity):
    # Get the predictions, title, and artist from the queried entity
    embeddings = entity[0]["predictions"]
    title = entity[0]["title"]
    artist = entity[0]["artist"]

    # Open and load the JSON file containing list of classes the model can predict
    with open('core/data/mtg_jamendo_genre.json', 'r') as json_file:
        metadata = json.load(json_file)

    classes = metadata.get('classes')
    embeddings = np.array(embeddings)
    if len(embeddings.shape) == 1:
        embeddings = embeddings.reshape(1, -1)

    average_activations = np.mean(embeddings, axis=0)
    average_activations_float = average_activations.astype(np.float32)
    sorted_indices = np.argsort(average_activations_float)
    top_5_classes = sorted_indices[-5:]
    top_5_activations = average_activations[top_5_classes]
    class_names = np.array(classes)[top_5_classes]

    return class_names, top_5_activations, title, artist


async def create_plot(class_names: List[str], top_5_activations: List[float], title: str, artist: str):
    fig, ax = plt.subplots(figsize=(6, 2))
    plt.barh(class_names, top_5_activations, color='#60a5fa', edgecolor='#cbd5e1')
    plt.title(f'Genres for {title} by {artist}', color='#cbd5e1')
    plt.tick_params(colors='#cbd5e1')
    ax.set_facecolor('#111827')
    fig.patch.set_facecolor('#111827')
    return fig


async def convert_plot_to_base64(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format='png')
    buf.seek(0)
    image_base64 = base64.b64encode(buf.read()).decode('utf-8')
    return image_base64