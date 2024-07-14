import os
import pickle
import tempfile

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from core.config import login_manager
from core.database import get_db
from models.openl3 import EmbeddingResponse
from services.minio import load_model_from_minio, get_temp_file_from_minio, get_embedding_pkl, save_embedding_pkl

router = APIRouter(prefix="/openl3")

@router.post("/embeddings/", response_model=EmbeddingResponse, tags=["OpenL3"])
def get_embeddings(file_path: str, user=Depends(login_manager), db: Session = Depends(get_db)):
    """
    Retrieves or computes the embeddings for a specified audio file.

    This function first checks if the embeddings for the specified audio file already exist as a .pkl file in MinIO.
    If they do, it returns them. If not, it loads a model from MinIO, retrieves the specified audio file as a temporary file,
    computes the embeddings using the loaded model, saves the embeddings to a .pkl file in MinIO, cleans up the temporary file,
    and then returns the embeddings. If the process fails, it raises an HTTPException with status code 500.

    Parameters:
    - file_path (str): The path to the audio file for which embeddings are to be computed or retrieved.
    - user: The current user object, automatically provided by the login_manager dependency.
    - db: The database session, automatically provided by the get_db dependency.

    Returns:
    - EmbeddingResponse: An object containing the file name and its computed or retrieved embeddings.
    """
    print(f"Starting to get embeddings for file: {file_path}")
    try:
        # Check if embeddings already exist
        existing_embeddings = get_embedding_pkl(file_path)
        if existing_embeddings:
            print(f"Embeddings for file: {file_path} retrieved from existing .pkl file.")
            return EmbeddingResponse(file_name=file_path, embedding=existing_embeddings)

        # Compute embeddings if not existing
        embedding_512_model = load_model_from_minio()
        temp_file_path = get_temp_file_from_minio(file_path)
        vector = embedding_512_model.compute(temp_file_path)
        embedding = vector.mean(axis=0)
        
        # Save embeddings to .pkl file in MinIO
        with tempfile.NamedTemporaryFile(delete=False) as temp_pkl:
            pickle.dump(embedding.tolist(), temp_pkl)
            temp_pkl.seek(0)
            save_embedding_pkl(file_path.replace(".mp3", ".pkl"), temp_pkl.name)
        
        # Clean up the temporary file
        os.unlink(temp_file_path)
        
        print(f"Successfully processed and saved embeddings for file: {file_path}")
        return EmbeddingResponse(file_name=file_path, embedding=embedding.tolist())
    except Exception as e:
        print(f"Failed to get embeddings for file: {file_path}. Error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to process the request: {e}")