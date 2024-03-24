from random import randint

from fastapi import APIRouter, HTTPException, Depends
from fastapi_login.exceptions import InvalidCredentialsException

from sqlalchemy import func
from sqlalchemy.dialects.postgresql import insert

from source.models.music import MusicLibrary, AddSongToMusicLibrary
from source.settings.config import SessionLocal, manager, DEFAULT_SETTINGS
from source.data.migrate_data import migrate_data_from_sqlite_to_postgres


router = APIRouter(prefix="/music_library")


@router.get("/count", tags=["songs"])
def count_rows():
    db = SessionLocal()
    try:
        count = db.query(MusicLibrary).count()
        return {"count": count}
    finally:
        db.close()


@router.get("/random", tags=["songs"])
def get_random_row():
    db = SessionLocal()
    try:
        count = db.query(MusicLibrary).count()
        random_id = randint(1, count)
        row = db.query(MusicLibrary).filter(MusicLibrary.id == random_id).first()
        return {"id": random_id, "row": row}
    finally:
        db.close()


@router.get("/{id}", tags=["songs"])
def get_row_by_id(id: str, user=Depends(manager)):
    db = SessionLocal()
    try:
        row = db.query(MusicLibrary).filter(MusicLibrary.id == id).first()
        if row is None:
            raise InvalidCredentialsException
        return {"id": id, "row": row}
    finally:
        db.close()


@router.get("/migrate_data", tags=["songs"])
def migrate_data(user=Depends(manager)):
    db = SessionLocal()
    try:
        migrate_data_from_sqlite_to_postgres(
            "source/data/music.db",
            DEFAULT_SETTINGS.database_url,
            DEFAULT_SETTINGS.postgre_music_table,
        )
        return {"message": "Data successfully migrated from SQLite to PostgreSQL"}
    finally:
        db.close()


@router.post("/add", tags=["songs"])
def add_row(query: AddSongToMusicLibrary, user=Depends(manager)):
    db = SessionLocal()
    try:
        # Get the maximum id from the music_library table
        max_id = db.query(func.max(MusicLibrary.id)).scalar()
        # If the table is empty, set max_id to 0
        if max_id is None:
            max_id = 0

        # insert into the table
        stmt = insert(MusicLibrary).values(
            id=max_id + 1,  # Set the id to one more than the current maximum
            filename=query.filename,
            filepath=query.filepath,
            album_folder=query.album_folder,
            artist_folder=query.artist_folder,
            filesize=query.filesize,
            title=query.title,
            artist=query.artist,
            album=query.album,
            year=query.year,
            tracknumber=query.tracknumber,
            genre=query.genre,
            top_5_genres=query.top_5_genres,
        )
        db.execute(stmt)
        db.commit()
        return {"message": "Row added successfully"}
    finally:
        db.close()


@router.delete("/delete/{id}", tags=["songs"])
def delete_row(id: int, user=Depends(manager)):
    db = SessionLocal()
    try:
        row = db.query(MusicLibrary).get(id)
        if row is None:
            raise HTTPException(status_code=404, detail="Row not found")
        db.delete(row)
        db.commit()
        return {"message": "Row deleted successfully"}
    finally:
        db.close()