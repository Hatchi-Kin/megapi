from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.sql import func

from models.music import MusicLibrary
from core.config import login_manager
from core.database import get_db
from services.lyrics import fetch_lyrics
from services.minio import get_artwork, convert_artwork_to_base64


router = APIRouter(prefix="/lyrics")


@router.get("/random-lyrics", tags=["lyrics"])
def get_random_row(user=Depends(login_manager), db: Session = Depends(get_db)):
    """
    Fetches a random song from the music library along with its lyrics from the lyrics.ovh API.

    - **user**: User - The authenticated user making the request.
    - **db**: Session - The database session for querying the database.
    - **return**: Returns a JSON object containing the song's ID, details, and lyrics.
    """
    with db:
        row = db.query(MusicLibrary).order_by(func.random()).first()
        if row is None:
            raise HTTPException(status_code=404, detail="No songs found in the library.")
        lyrics = fetch_lyrics(row.artist, row.title)
        return {"id": row.id, "row": row, "lyrics": lyrics}
    

@router.get("/random-lyrics-metadata", tags=["lyrics"])
def get_random_row_and_lyrics_and_metadata(user=Depends(login_manager), db: Session = Depends(get_db)):
    """
    Fetches a random song from the music library along with its lyrics and metadata including artwork.

    - **user**: User - The authenticated user making the request.
    - **db**: Session - The database session for querying the database.
    - **return**: Returns a JSON object containing the song's ID, details, lyrics from the lyrics.ovh API, and artwork from the metadata.
    """
    with db:
        row = db.query(MusicLibrary).order_by(func.random()).first()
        if row is None:
            raise HTTPException(status_code=404, detail="No songs found in the library.")
        lyrics = fetch_lyrics(row.artist, row.title)
        artwork = get_artwork("megasetbucket", row.filepath)
        return {"id": row.id, "row": row, "lyrics": lyrics, "artwork": artwork}