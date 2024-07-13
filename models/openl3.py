"""models/openl3.py
Defines Pydantic models for handling song lists and embedding responses.

This module is designed to structure the data for song list inputs and their corresponding embedding outputs, facilitating the interaction with machine learning models or APIs that generate embeddings for songs.
"""

from pydantic import BaseModel


class SongList(BaseModel):
    """
    Pydantic model for a list of songs.

    Attributes:
        songs (list): A list of song identifiers or paths.
    """
    songs: list


class EmbeddingResponse(BaseModel):
    """
    Pydantic model for the response containing embeddings for a song.

    Attributes:
        file_name (str): The name of the file for which the embedding was generated.
        embedding (list): The generated embedding as a list of floats.
    """
    file_name: str
    embedding: list
