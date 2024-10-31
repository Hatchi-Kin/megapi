import os
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from models.music import SongPath
from core.config import login_manager, DEFAULT_SETTINGS
from services.minio import get_temp_file_from_minio, get_metadata_and_artwork
from services.milvus import get_milvus_87_collection, extract_plot_data, create_plot, convert_plot_to_base64
from services.music_net import create_preprocessed_spectrogram, get_production_model, predict_with_production_music_net

router = APIRouter(prefix="/elo")

async def get_model_predictions(file_path: str):
    model = get_production_model()
    if model is None:
        raise HTTPException(status_code=500, detail="Failed to load the production model.")
    
    temp_file_path = get_temp_file_from_minio(file_path)
    try:
        img_tensor = create_preprocessed_spectrogram(temp_file_path)
        if img_tensor is None:
            raise HTTPException(status_code=500, detail="Failed to create the preprocessed spectrogram.")
        genre = predict_with_production_music_net(model, img_tensor)
    finally:
        os.remove(temp_file_path)
    
    return genre

async def get_essentia_predictions(file_path: str):
    collection_87 = get_milvus_87_collection()
    entity = collection_87.query(
        expr=f"path == '{file_path}'",
        output_fields=["predictions", "title", "artist"], 
        limit=1
    )
    if not entity:
        raise HTTPException(status_code=404, detail="Entity not found")
    
    class_names, top_5_activations, title, artist = await extract_plot_data(entity)
    fig = await create_plot(class_names, top_5_activations, title, artist)
    predictions_plot = await convert_plot_to_base64(fig)
    
    return predictions_plot



@router.post("/compare_models", tags=["elo"])
async def get_comparison(query: SongPath, user=Depends(login_manager)):
    try:
        # 1. Get the metadata and artwork from MinIO
        metadata = get_metadata_and_artwork(DEFAULT_SETTINGS.minio_bucket_name, query.file_path)

        # 2. Get the predictions from the model from mlflow and add them to the metadata
        metadata['prediction_model_1'] = await get_model_predictions(query.file_path)

        # 3. Get the predictions from the model from essentia
        metadata['predictions_openl3'] = await get_essentia_predictions(query.file_path)

        # Return the combined metadata and predictions
        return JSONResponse(content=metadata)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))