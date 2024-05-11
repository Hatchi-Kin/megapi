from sqlalchemy.orm import Session

from models.music import MusicLibrary, SongPath


def get_song_id_by_filepath(db: Session, file_path: SongPath):
    song = db.query(MusicLibrary).filter(MusicLibrary.filepath == file_path).first()
    if song:
        return song.id
    else:
        return None