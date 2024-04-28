from typing import List, Dict
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from core.config import login_manager
from core.database import get_db
from models.spotinite import SpotiniteQuery, SpotiniteResponse
from services.spotinite import get_track_id, fetch_similar_tracks, get_track_info


router = APIRouter(prefix="/spotinite")


@router.post("/similar_tracks", response_model=List[SpotiniteResponse])
async def similar_tracks(query: SpotiniteQuery, user=Depends(login_manager), db: Session = Depends(get_db)):
    """Return similar tracks based on the input song and artist."""
    try:
        spotify_id = get_track_id(query.title, query.artist)
        similar_track_ids = fetch_similar_tracks(spotify_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    similar_tracks = []
    for track_id in similar_track_ids:
        track_info = get_track_info(track_id)
        if track_info['Artist'] != query.artist:
            similar_tracks.append(track_info)
            if len(similar_tracks) == 3:
                break

    return similar_tracks