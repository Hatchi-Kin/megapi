from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.sql import func

from models.music import MusicLibrary
from core.config import login_manager
from core.database import get_db
from services.lyrics import fetch_lyrics


router = APIRouter(prefix="/lyrics")


@router.get("/random-lyrics", tags=["lyrics"])
def get_random_row(user=Depends(login_manager), db: Session = Depends(get_db)):
    """Return a random row from the music_library table and lyrics from the lyrics.ovh API."""
    with db:
        row = db.query(MusicLibrary).order_by(func.random()).first()
        if row is None:
            raise HTTPException(status_code=404, detail="No songs found in the library.")
        lyrics = fetch_lyrics(row.artist, row.title)
        return {"id": row.id, "row": row, "lyrics": lyrics}