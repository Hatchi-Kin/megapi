from typing import List

from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from minio import Minio

from core.config import login_manager, minio_client, DEFAULT_SETTINGS
from models.minio import S3Object
from models.music import AlbumResponse, SongPath


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