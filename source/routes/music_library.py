from random import randint

from fastapi import APIRouter, HTTPException, Depends
from fastapi_login.exceptions import InvalidCredentialsException

from sqlalchemy import func
from sqlalchemy.dialects.postgresql import insert
from typing import Optional

from source.models.music import (
    MusicLibrary,
    AddSongToMusicLibrary,
    AlbumResponse,
    ArtistFolderResponse,
)
from source.settings.config import SessionLocal, login_manager, DEFAULT_SETTINGS
from source.data.migrate_data import migrate_data_from_sqlite_to_postgres


router = APIRouter(prefix="/music_library")


@router.get("/count", tags=["songs"])
def count_rows():
    """
    Return the number of rows in the music_library table.
    """
    db = SessionLocal()
    try:
        count = db.query(MusicLibrary).count()
        return count
    finally:
        db.close()


@router.get("/random", tags=["songs"])
def get_random_row():
    """
    Return a random row from the music_library table.
    """
    db = SessionLocal()
    try:
        count = db.query(MusicLibrary).count()
        random_id = randint(1, count)
        row = db.query(MusicLibrary).filter(MusicLibrary.id == random_id).first()
        return {"id": random_id, "row": row}
    finally:
        db.close()


@router.get("/song/{id}", tags=["songs"])
def get_row_by_id(id: str, user=Depends(login_manager)):
    """
    Return a row from the music_library table by it's id.
    """
    db = SessionLocal()
    try:
        row = db.query(MusicLibrary).filter(MusicLibrary.id == id).first()
        if row is None:
            raise InvalidCredentialsException
        return {"id": id, "row": row}
    finally:
        db.close()


@router.get("/migrate_data", tags=["songs"])
def migrate_data(user=Depends(login_manager)):
    """
    Migrate data from the SQLite database to the PostgreSQL database.
    """
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
def add_row(query: AddSongToMusicLibrary, user=Depends(login_manager)):
    """
    Add a row to the music_library table.
    """
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
def delete_row(id: int, user=Depends(login_manager)):
    """
    Delete a row from the music_library table by it's id.
    """
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


########################## Flask ##########################


@router.get("/artists", tags=["songs"])
def list_all_artists(user=Depends(login_manager)):
    """
    Return a list of all artists in alphabetical order.
    """
    db = SessionLocal()
    try:
        query = (
            db.query(MusicLibrary.artist_folder)
            .distinct()
            .order_by(MusicLibrary.artist_folder.asc())
        )
        return [row.artist_folder for row in query.all()]
    finally:
        db.close()


@router.post("/albums", tags=["songs"])
def list_all_albums_from_artist(
    artist_folder: ArtistFolderResponse, user=Depends(login_manager)
):
    """
    Return a list of all albums for a given artist in release date order.
    """
    if artist_folder is None or artist_folder.artist_folder is None:
        raise HTTPException(status_code=400, detail="Missing artist_folder parameter")

    db = SessionLocal()

    try:
        query = (
            db.query(MusicLibrary.album, MusicLibrary.album_folder, MusicLibrary.year)
            .filter(MusicLibrary.artist_folder == artist_folder.artist_folder)
            .distinct()
            .order_by(MusicLibrary.year.asc())
        )
        return [row.album for row in query.all()]

    finally:
        db.close()


@router.post("/songs", tags=["songs"])
def list_all_songs_from_album(
    album_folder: AlbumResponse = None, user=Depends(login_manager)
):
    """
    Return a list of all songs for a given album by a given artist.
    """
    if album_folder is None or album_folder.album_folder is None:
        raise HTTPException(status_code=400, detail="Missing album_folder parameter")

    db = SessionLocal()

    try:
        query = db.query(MusicLibrary).filter(
            MusicLibrary.album_folder == album_folder.album_folder,
        )

        # return the tracknumber and title of each song in order of tracknumber
        return [
            {"tracknumber": row.tracknumber, "title": row.title}
            for row in query.order_by(MusicLibrary.tracknumber.asc()).all()
        ]

    finally:
        db.close()
