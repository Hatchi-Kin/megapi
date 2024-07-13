"""models/spotinite.py

Enhances the SpotiniteQuery and SpotiniteResponse models with additional documentation and validation.

This module defines the structure for queries to and responses from a hypothetical Spotinite service, which appears to be a music information retrieval system.
"""

from pydantic import BaseModel, Field


class SpotiniteQuery(BaseModel):
    """
    Represents a query to the Spotinite service for song information.

    Attributes:
        title (str): The title of the song to query.
        artist (str): The artist of the song to query.
    """
    title: str = Field(..., description="The title of the song")
    artist: str = Field(..., description="The artist of the song")


class SpotiniteResponse(BaseModel):
    """
    Represents a response from the Spotinite service with song information.

    Attributes:
        Track_Name (str): The name of the track.
        Artist (str): The artist of the track.
        Album (str): The album on which the track appears.
        URI (str): A unique resource identifier for the track, possibly for streaming or further reference.
        Cover_Image (str): A URL or a base64 encoded string of the cover image for the track.
    """
    Track_Name: str = Field(..., alias="Track Name")
    Artist: str
    Album: str
    URI: str
    Cover_Image: str = Field(..., alias="Cover Image")
