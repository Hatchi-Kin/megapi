from fastapi import APIRouter, HTTPException, Depends
import torch
from core.config import login_manager
from services.music_net import create_preprocessed_spectrogram, get_production_model, predict_with_production_music_net, MAPPING_DICT_MUSIC_NET

router = APIRouter(prefix="/music_net")


GenrePredictionResponse = {
    "genre": str,
}

@router.post("/predict-genre/", response_model=GenrePredictionResponse, tags=["music_net"])
def predict_genre(audio_path: str, user=Depends(login_manager)):
    """
    Predicts the genre of a music segment using a pre-trained MusicNet model.

    - **audio_path**: str - The path to the audio file.
    - **start_time**: int - The start time of the segment.
    - **segment_duration**: int - The duration of the segment.
    - **return**: dict - A dictionary containing the predicted genre and the corresponding probability.
    """
    try:
        # Load the production model
        model = get_production_model()
        if model is None:
            raise HTTPException(status_code=500, detail="Failed to load the production model.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading model: {e}")

    try:
        # Create a preprocessed spectrogram
        img_tensor = create_preprocessed_spectrogram(audio_path)
        if img_tensor is None:
            raise HTTPException(status_code=500, detail="Failed to create the preprocessed spectrogram.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating spectrogram: {e}")

    try:
        # Predict the genre
        genre = predict_with_production_music_net(model, img_tensor)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error predicting genre: {e}")

    return {"genre": genre}