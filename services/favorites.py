from sqlalchemy.orm import Session

from models.music import MusicLibrary, SongPath


def get_song_id_by_filepath(db: Session, file_path: SongPath) -> int:
    """
    Retrieves the ID of a song from the MusicLibrary table based on its file path.

    Args:
        db (Session): The SQLAlchemy session for database access.
        file_path (SongPath): The file path of the song.

    Returns:
        int: The ID of the song if found, otherwise None.
    """
    song = db.query(MusicLibrary).filter(MusicLibrary.filepath == file_path).first()
    if song:
        return song.id
    else:
        return None
