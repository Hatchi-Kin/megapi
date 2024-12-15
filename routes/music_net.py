import os
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
import torch

from core.config import login_manager
from models.openl3 import PathForEmbedding
from services.minio import get_temp_file_from_minio
from services.music_net import create_preprocessed_spectrogram, get_production_model, predict_with_production_music_net

router = APIRouter(prefix="/music_net")


class GenrePredictionResponse(BaseModel):
    genre: str

@router.post("/predict-genre/", response_model=GenrePredictionResponse, tags=["music_net"])
def predict_genre(query: PathForEmbedding, user=Depends(login_manager)):
    """
    Predicts the genre of a music segment using a pre-trained MusicNet model.

    - **audio_path**: str - The path to the audio file in the MinIO bucket.
    - **return**: dict - A dictionary containing the predicted genre.
    """
    try:
        # Load the production model
        model = get_production_model()
        if model is None:
            raise HTTPException(status_code=500, detail="Failed to load the production model.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading model: {e}")

    try:
        # Retrieve the MP3 file from MinIO and write it to a temporary file
        temp_file_path = get_temp_file_from_minio(query.file_path)

        # Create a preprocessed spectrogram
        img_tensor = create_preprocessed_spectrogram(temp_file_path)
        if img_tensor is None:
            raise HTTPException(status_code=500, detail="Failed to create the preprocessed spectrogram.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating spectrogram: {e}")

    try:
        # Predict the genre
        genre = predict_with_production_music_net(model, img_tensor)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error predicting genre: {e}")
    finally:
        # Clean up the temporary file
        os.remove(temp_file_path)

    return {"genre": genre}