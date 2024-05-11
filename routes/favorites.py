from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from core.database import get_db
from core.config import login_manager
from models.users import User
from models.music import MusicLibrary, SongPath
from services.favorites import get_song_id_by_filepath


router = APIRouter(prefix="/favorites")


@router.get("/", tags=["favorites"])
async def get_favorites(user=Depends(login_manager), db: Session = Depends(get_db)):
    # The merge() function is used to merge a detached object back into the session.
    # It returns a new instance that represents the existing row in the DB.
    # This is necessary because the 'user' object might have been created in a different session and we want to associate it with the current session.
    user = db.merge(user)

    # The refresh() function is used to update the attributes of the 'user' instance with the current data in the DB.
    # This is necessary because the 'user' object might have stale data and we want to ensure we're working with the most recent data.
    db.refresh(user)
    return user.favorites


@router.post("/add", tags=["favorites"])
async def add_song_to_favorites(song: SongPath, user: User = Depends(login_manager), db: Session = Depends(get_db)):
    user = db.merge(user)
    db.refresh(user)

    if len(user.favorites) >= 9:
        # Remove the oldest song from the favorites
        user.favorites.pop(0)

    music_id = get_song_id_by_filepath(db, song.file_path)
    if not music_id:
        raise HTTPException(status_code=404, detail="Song not found")
    music = db.query(MusicLibrary).get(music_id)
    user.favorites.append(music)
    db.commit()
    return {"message": "Song added to favorites"}


@router.delete("/delete", tags=["favorites"])
async def delete_song_from_favorites(song: SongPath, user: User = Depends(login_manager), db: Session = Depends(get_db)):
    user = db.merge(user)
    db.refresh(user)
    music_id = get_song_id_by_filepath(db, song.file_path)
    if not music_id:
        raise HTTPException(status_code=404, detail="Song not found")
    music = db.query(MusicLibrary).get(music_id)
    if music in user.favorites:
        user.favorites.remove(music)
        db.commit()
    return {"message": "Song removed from favorites"}