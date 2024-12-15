import os
import pickle
import tempfile
from datetime import datetime
import time

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from core.config import login_manager
from core.database import get_db
from models.openl3 import EmbeddingResponse, OpenL3ComputationLog, PathForEmbedding
from services.minio import load_model_from_minio, get_temp_file_from_minio, get_embedding_pkl, save_embedding_pkl


router = APIRouter(prefix="/openl3")


@router.post("/embeddings/", response_model=EmbeddingResponse, tags=["OpenL3"])
def get_embeddings(file_path: PathForEmbedding, user=Depends(login_manager), db: Session = Depends(get_db)):
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
    start_time = time.time()
    try:
        existing_embeddings = get_embedding_pkl(file_path)
        if existing_embeddings:
            return EmbeddingResponse(file_name=file_path, embedding=existing_embeddings)

        embedding_512_model = load_model_from_minio()
        temp_file_path = get_temp_file_from_minio(file_path)
        vector = embedding_512_model.compute(temp_file_path)
        embedding = vector.mean(axis=0)
        
        with tempfile.NamedTemporaryFile(delete=False) as temp_pkl:
            pickle.dump(embedding.tolist(), temp_pkl)
            temp_pkl.seek(0)
            save_embedding_pkl(file_path.replace(".mp3", ".pkl"), temp_pkl.name)
        
        os.unlink(temp_file_path)

        # Log the computation activity
        computation_time_ms = (time.time() - start_time) * 1000
        log_entry = OpenL3ComputationLog(
            user_id=user.id,
            datetime=datetime.now(),
            file_path=file_path,
            model_version="V1", # Hardcoded model version for now
            response_time_ms=computation_time_ms
        )
        db.add(log_entry)
        db.commit()

        return EmbeddingResponse(file_name=file_path, embedding=embedding.tolist())
    except Exception as e:
        error_message = str(e)
        db.rollback()
        # Create a log entry with the error message
        log_entry = OpenL3ComputationLog(
            user_id=user.id,
            datetime=datetime.now(),
            file_path=file_path,
            model_version="V1",  # 
            response_time_ms=0,  # Set to 0 since the computation failed
            error_message=error_message 
        )
        db.add(log_entry)
        db.commit()
        raise HTTPException(status_code=500, detail=f"Failed to process the request: {error_message}")