"""services/milvus.py

This Python module provides a comprehensive suite of functionalities for interacting with the Milvus vector database, specifically tailored for managing and querying music-related data. 
It includes capabilities for connecting to Milvus, performing queries, and processing the results for further analysis or visualization. 
Additionally, it offers utilities for generating visual representations of data, such as genre predictions for music tracks, and converting these visualizations into a format suitable for web display.

"""

import io
import base64
from typing import List
import json

import numpy as np
import matplotlib.pyplot as plt
from pymilvus import Collection, connections

from core.config import DEFAULT_SETTINGS


def ping_milvus():
    """
    Attempts to connect to the Milvus database using settings from the configuration and performs a simple query to check if the connection is successful.

    Returns:
        A dictionary with a status message indicating the outcome of the connection attempt.
    """
    try:
        connections.connect(
            "default",
            uri=DEFAULT_SETTINGS.milvus_uri,
            token=DEFAULT_SETTINGS.milvus_api_key,
        )
        embedding_512 = Collection(name=DEFAULT_SETTINGS.milvus_512_collection_name)
        response = embedding_512.query(
            expr="id in [0]",
            output_fields=["artist"],
        )
        if response:
            return {"status": "success", "message": "Milvus is running"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


def get_milvus_512_collection():
    """
    Connects to the Milvus database and retrieves the collection specified for 512-dimensional vectors.

    Returns:
        The Milvus Collection object corresponding to the 512-dimensional vector collection.
    """
    connections.connect(
        "default",
        uri=DEFAULT_SETTINGS.milvus_uri,
        token=DEFAULT_SETTINGS.milvus_api_key,
    )
    return Collection(name=DEFAULT_SETTINGS.milvus_512_collection_name)


def get_milvus_87_collection():
    """
    Connects to the Milvus database and retrieves the collection specified for 87-dimensional vectors.

    Returns:
        The Milvus Collection object corresponding to the 87-dimensional vector collection.
    """
    connections.connect(
        "default",
        uri=DEFAULT_SETTINGS.milvus_uri,
        token=DEFAULT_SETTINGS.milvus_api_key,
    )
    return Collection(name=DEFAULT_SETTINGS.milvus_87_collection_name)


def full_hit_to_dict(hit):
    """
    Converts the full details of a Milvus query hit into a dictionary format, including all available entity information.

    Args:
        hit: The query hit object returned by Milvus.

    Returns:
        A dictionary containing detailed information about the query hit.
    """
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
    """
    Converts a Milvus query hit into a simplified dictionary format, focusing on essential metadata.

    Args:
        hit: The query hit object returned by Milvus.

    Returns:
        A simplified dictionary containing key information about the query hit.
    """
    return {
        "title": hit.entity.title,
        "album": hit.entity.album,
        "artist": hit.entity.artist,
        "path": hit.entity.path,
    }


def sort_entities(entities):
    """
    Sorts a list of entities based on artist uniqueness to prioritize diversity in recommendations.

    Args:
        entities: A list of entities (query hits) to be sorted.

    Returns:
        A sorted list of entities with unique artists prioritized.
    """
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
    if len(response_list) < 9:
        response_list.extend(fallback_list[:9-len(response_list)])
    return response_list


async def extract_plot_data(entity):
    """
    Extracts data from a single entity for the purpose of generating a genre prediction plot.

    Args:
        entity: The entity from which to extract plot data.

    Returns:
        A tuple containing class names, top 5 activations, title, and artist, ready for plotting.
    """
    embeddings = entity[0]["predictions"]
    title = entity[0]["title"]
    artist = entity[0]["artist"]

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
    """
    Generates a horizontal bar plot visualizing the top 5 music genre predictions for a given track.

    Args:
        class_names: The names of the top 5 predicted genres.
        top_5_activations: The activation values for the top 5 predicted genres.
        title: The title of the music track.
        artist: The artist of the music track.

    Returns:
        A matplotlib figure object containing the generated plot.
    """
    fig, ax = plt.subplots(figsize=(6, 2))
    plt.barh(class_names, top_5_activations, color='#60a5fa', edgecolor='#cbd5e1')
    plt.title(f'Genres for {title} by {artist}', color='#cbd5e1')
    plt.tick_params(colors='#cbd5e1')
    ax.set_facecolor('#111827')
    fig.patch.set_facecolor('#111827')
    return fig


async def convert_plot_to_base64(fig):
    """
    Converts a matplotlib plot to a base64-encoded string for embedding in web pages or other digital formats.

    Args:
        fig: The matplotlib figure to convert.

    Returns:
        A base64-encoded string representing the plot image.
    """
    buf = io.BytesIO()
    fig.savefig(buf, format='png')
    buf.seek(0)
    image_base64 = base64.b64encode(buf.read()).decode('utf-8')
    return image_base64
