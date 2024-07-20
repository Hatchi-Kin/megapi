import os
from typing import List
from random import randint

from sqlalchemy.orm import Session
from fastapi import APIRouter, HTTPException, UploadFile, File, Depends
from fastapi.responses import StreamingResponse, JSONResponse
from minio.error import S3Error

from core.config import login_manager, minio_client, DEFAULT_SETTINGS
from core.database import get_db
from models.minio import S3Object, UploadMP3ResponseList, UploadDetail
from models.music import AlbumResponse, SongPath, MusicLibrary
from services.minio import get_metadata_and_artwork, sanitize_filename
from services.uploaded import store_upload_info, get_user_uploads, delete_user_upload_from_db


router = APIRouter(prefix="/minio")


@router.post("/list-objects/", response_model=List[S3Object], tags=["MinIO"])
def list_objects_in_album_folder(query: AlbumResponse, user=Depends(login_manager)):
    """
    Retrieves a list of objects within a specified album folder in the MinIO bucket.

    - **query**: AlbumResponse - The album folder to list objects from.
    - **user**: User - The authenticated user making the request.
    - **return**: List[S3Object] - A list of objects found in the specified album folder.
    """
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


@router.post("/list-uploaded-objects", response_model=UploadMP3ResponseList, tags=["MinIO"])
def list_uploaded_objects(user=Depends(login_manager), db: Session = Depends(get_db)):
    """
    Lists objects uploaded by the authenticated user.

    - **user**: User - The authenticated user making the request.
    - **db**: Session - Database session dependency.
    - **return**: UploadMP3ResponseList - A list of uploaded objects by the user.
    """
    objects = minio_client.list_objects(DEFAULT_SETTINGS.minio_temp_bucket_name)
    # Adjusting the response to match the expected structure
    uploads = [UploadDetail(filename=obj.object_name) for obj in objects]
    response = UploadMP3ResponseList(uploads=uploads)
    return response


@router.post("/stream-song/", tags=["MinIO"])
async def get_file(query: SongPath, user=Depends(login_manager)):
    """
    Streams a song file from MinIO storage.

    - **query**: SongPath - The path to the song file in MinIO storage.
    - **user**: User - The authenticated user making the request.
    - **return**: StreamingResponse - A streaming response of the song file.
    """
    try:
        data = minio_client.get_object(DEFAULT_SETTINGS.minio_bucket_name, query.file_path)
        return StreamingResponse(data.stream(32*1024), media_type="audio/mpeg")
    except Exception as e:
        raise HTTPException(status_code=404, detail="File not found")
    

@router.post("/download-song/", tags=["MinIO"])
async def download_file(query: SongPath, user=Depends(login_manager)):
    """
    Downloads a song file from MinIO storage.

    - **query**: SongPath - The path to the song file in MinIO storage.
    - **user**: User - The authenticated user making the request.
    - **return**: StreamingResponse - A streaming response for downloading the song file.
    """
    try:
        data = minio_client.get_object(DEFAULT_SETTINGS.minio_bucket_name, query.file_path)
        filename = query.file_path.split('/')[-1]  # Get the filename from the file_path
        headers = {
            "Content-Disposition": f"attachment; filename={filename}",
        }
        return StreamingResponse(data.stream(32*1024), media_type="audio/mpeg", headers=headers)
    except Exception as e:
        raise HTTPException(status_code=404, detail="File not found")
    

@router.post("/metadata", tags=["MinIO"])
async def get_song_metadata(query: SongPath, user=Depends(login_manager)):
    """
    Retrieves metadata for a specified song from MinIO storage using the music-tag library.

    - **query**: SongPath - The path to the song file in MinIO storage.
    - **user**: User - The authenticated user making the request.
    - **return**: JSONResponse - The metadata of the specified song.
    """
    try:
        metadata = get_metadata_and_artwork(DEFAULT_SETTINGS.minio_bucket_name, query.file_path)
        return JSONResponse(content=metadata)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    

@router.get("/random-metadata", tags=["MinIO"])
async def get_random_song_metadata(user=Depends(login_manager), db: Session = Depends(get_db)):
    """
    Retrieves metadata for a random song from MinIO storage using the music-tag library.

    - **user**: User - The authenticated user making the request.
    - **db**: Session - Database session dependency.
    - **return**: JSONResponse - The metadata of a random song.
    """
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


@router.post("/upload-temp", tags=["MinIO"], response_model=UploadMP3ResponseList)
async def upload_file(file: UploadFile = File(...), user=Depends(login_manager), db: Session = Depends(get_db)):
    """
    Uploads a MP3 file to MinIO storage using a temporary bucket.

    - **file**: UploadFile - The MP3 file to upload.
    - **user**: User - The authenticated user making the request.
    - **db**: Session - Database session dependency.
    - **return**: UploadMP3ResponseList - A list of uploaded MP3 files by the user.
    """
    try: 
        if file.content_type != "audio/mpeg":
            raise HTTPException(status_code=400, detail="Only MP3 files are allowed.")
        _, file_extension = os.path.splitext(file.filename)
        if file_extension.lower() != ".mp3":
            raise HTTPException(status_code=400, detail="The uploaded file is not an MP3 file.")

        secure_filename = sanitize_filename(file.filename)

        # Determine the size of the uploaded file by moving the cursor to the end to get the file size
        file.file.seek(0, os.SEEK_END)  
        file_size = file.file.tell() 
        file.file.seek(0)  

        # Stream the file directly to MinIO
        minio_client.put_object(
            bucket_name=DEFAULT_SETTINGS.minio_temp_bucket_name,
            object_name=secure_filename,
            data=file.file,
            length=file_size,
            content_type=file.content_type
        )

        # Store upload information in the database and return the updated list of uploaded songs by the user
        # song_path_in_minio = f"{DEFAULT_SETTINGS.minio_temp_bucket_name}/{secure_filename}"
        store_upload_info(db, user.id, secure_filename)
        uploaded_songs = get_user_uploads(db, user.id)

        return UploadMP3ResponseList(uploads=uploaded_songs)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred. {str(e)}")
    

@router.post("/delete-temp", tags=["MinIO"], response_model=UploadMP3ResponseList)
async def delete_temp_file(query: SongPath, user=Depends(login_manager), db: Session = Depends(get_db)):
    """
    Deletes a MP3 file from MinIO bucket.

    - **query**: SongPath - The path to the MP3 file in MinIO storage.
    - **user**: User - The authenticated user making the request.
    - **db**: Session - Database session dependency.
    - **return**: UploadMP3ResponseList - A list of uploaded MP3 files by the user.
    """
    try:
        minio_client.remove_object(DEFAULT_SETTINGS.minio_temp_bucket_name, query.file_path)
        # Also delete the upload information from the database and return the updated list of uploaded songs by the user
        delete_user_upload_from_db(db, user.id, query.file_path)

        uploaded_songs = get_user_uploads(db, user.id)
        return UploadMP3ResponseList(uploads=uploaded_songs)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred. {str(e)}")
    

@router.get("/minio/emb_extracted/{filename}")
async def check_embeddings_extracted(filename: str):
    """
    Checks if embeddings have been extracted for a given filename in MinIO.

    - **filename**: str - The filename to check for embeddings extraction.
    - **return**: dict - A dictionary containing the status of embeddings extraction.
    """
    try:
        pkl_file = filename.rsplit(".", 1)[0] + ".pkl"
        minio_client.get_object(DEFAULT_SETTINGS.minio_temp_bucket_name, pkl_file)
        embeddings_extracted = True
    except S3Error as e:
        if e.code == "NoSuchKey":
            embeddings_extracted = False
        else:
            raise HTTPException(status_code=500, detail="Unexpected server error")
    except Exception as e:
        print(f"Unexpected error when checking embeddings for {filename}: {e}")
        embeddings_extracted = False

    return {"extracted": embeddings_extracted}
