import os
from typing import List
from random import randint

from sqlalchemy.orm import Session
from fastapi import APIRouter, HTTPException, UploadFile, File, Depends
from fastapi.responses import StreamingResponse, JSONResponse

from core.config import login_manager, minio_client, DEFAULT_SETTINGS
from models.minio import S3Object, UploadMP3Response
from models.music import AlbumResponse, SongPath, MusicLibrary
from services.minio import get_metadata_and_artwork, sanitize_filename
from core.database import get_db

router = APIRouter(prefix="/minio")


@router.post("/list-objects/", response_model=List[S3Object], tags=["miniO"])
def list_objects_in_album_folder(query: AlbumResponse, user=Depends(login_manager)):
    """Get a list of object in the given album_folder of megasetbucket."""
    objects = minio_client.list_objects(
        DEFAULT_SETTINGS.minio_bucket_name,
        prefix=query.album_folder,
        recursive=True)

    response = []
    for obj in objects:
        s3_object = {
            "name": obj.object_name,
            "size": obj.size,
            "etag": obj.etag,
            "last_modified": obj.last_modified.isoformat()
        }
        response.append(s3_object)

    return response


@router.post("/stream-song/", tags=["miniO"])
async def get_file(query: SongPath, user=Depends(login_manager)):
    """Stream a file from MinIO storage."""
    try:
        data = minio_client.get_object(DEFAULT_SETTINGS.minio_bucket_name, query.file_path)
        return StreamingResponse(data.stream(32*1024), media_type="audio/mpeg")
    except Exception as e:
        raise HTTPException(status_code=404, detail="File not found")
    

@router.post("/download-song/", tags=["miniO"])
async def download_file(query: SongPath, user=Depends(login_manager)):
    """Download a file from MinIO storage."""
    try:
        data = minio_client.get_object(DEFAULT_SETTINGS.minio_bucket_name, query.file_path)
        filename = query.file_path.split('/')[-1]  # Get the filename from the file_path
        headers = {
            "Content-Disposition": f"attachment; filename={filename}",
        }
        return StreamingResponse(data.stream(32*1024), media_type="audio/mpeg", headers=headers)
    except Exception as e:
        raise HTTPException(status_code=404, detail="File not found")
    

@router.post("/metadata", tags=["miniO"])
async def get_song_metadata(query: SongPath, user=Depends(login_manager)):
    """Get the metadata of a given song_path from MinIO storage using music_tag."""
    try:
        metadata = get_metadata_and_artwork(DEFAULT_SETTINGS.minio_bucket_name, query.file_path)
        return JSONResponse(content=metadata)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    

@router.get("/random-metadata", tags=["miniO"])
async def get_random_song_metadata(user=Depends(login_manager), db: Session = Depends(get_db)):
    """Get a random song with metadata from MinIO storage using music_tag."""
    try:
        count = db.query(MusicLibrary).count()
        random_id = randint(1, count)
        row = db.query(MusicLibrary).filter(MusicLibrary.id == random_id).first()
        metadata = get_metadata_and_artwork(DEFAULT_SETTINGS.minio_bucket_name, row.filepath)
        return JSONResponse(content=metadata)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        db.close()


@router.post("/upload-temp", tags=["MinIO"], response_model=UploadMP3Response)
async def upload_file(file: UploadFile = File(...)):
    try:   # Check content type and extension
        if file.content_type != "audio/mpeg":
            raise HTTPException(status_code=400, detail="Only MP3 files are allowed.")
        _, file_extension = os.path.splitext(file.filename)
        if file_extension.lower() != ".mp3":
            raise HTTPException(status_code=400, detail="The uploaded file is not an MP3 file.")

        # Generate a secure filename
        secure_filename = sanitize_filename(file.filename)

        # Stream the file directly to MinIO
        await minio_client.put_object(
            bucket_name=DEFAULT_SETTINGS.minio_temp_bucket_name,
            object_name=secure_filename,
            data=file.file,
            length=-1,  # Use -1 for unknown size to stream efficiently
            content_type=file.content_type
        )

        return UploadMP3Response(filename=secure_filename)
    except HTTPException:
        # Re-raise FastAPI's HTTPException without modification
        raise
    except Exception as e:
        # Log the exception details here for debugging
        raise HTTPException(status_code=500, detail="An unexpected error occurred.")