from fastapi import APIRouter
from source.models.music import MusicLibrary
from source.dependencies.config import SessionLocal


router = APIRouter(prefix="/music_library")

@router.get("/count", tags=["songs"])
def count_rows():
    db = SessionLocal()
    try:
        count = db.query(MusicLibrary).count()
        return {"count": count}
    finally:
        db.close()