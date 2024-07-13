from pydantic import BaseModel, Field


class SpotiniteQuery(BaseModel):
    title: str = Field(..., description="The title of the song")
    artist: str = Field(..., description="The artist of the song")


class SpotiniteResponse(BaseModel):
    Track_Name: str = Field(..., alias="Track Name")
    Artist: str
    Album: str
    URI: str
    Cover_Image: str = Field(..., alias="Cover Image")
