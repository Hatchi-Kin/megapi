# import os

# from fastapi import APIRouter, Depends, HTTPException
# from sqlalchemy.orm import Session

# from core.config import login_manager, DEFAULT_SETTINGS
# from core.database import get_db
# from models.openl3 import EmbeddingResponse
# from services.minio import load_model_from_minio, get_temp_file_from_minio


# router = APIRouter(prefix="/openl3")


# @router.post("/embeddings/", response_model=EmbeddingResponse, tags=["OpenL3"])
# def get_embeddings(file_path: str, user=Depends(login_manager), db: Session = Depends(get_db)):
#     """Get embeddings of an audio file."""
#     print(f"Starting to get embeddings for file: {file_path}")
#     # full_path = f"{DEFAULT_SETTINGS.minio_openl3_bucket_name}/{file_path}"
#     try:
#         embedding_512_model = load_model_from_minio()
#         temp_file_path = get_temp_file_from_minio(file_path)
        
#         # Compute embeddings using the temporary file path
#         vector = embedding_512_model.compute(temp_file_path)
#         embedding = vector.mean(axis=0)
        
#         # Clean up the temporary file
#         os.unlink(temp_file_path)
        
#         print(f"Successfully processed embeddings for file: {file_path}")
#         return EmbeddingResponse(file_name=file_path, embedding=embedding.tolist())
#     except Exception as e:
#         print(f"Failed to get embeddings for file: {file_path}. Error: {e}")
#         raise HTTPException(status_code=500, detail=f"Failed to process the request: {e}")