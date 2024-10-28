import pytest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from core.config import Base
from services.favorites import get_song_id_by_filepath
from models.music import MusicLibrary


@pytest.fixture(scope='function')
def db_session():
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    # Add some sample data
    song1 = MusicLibrary(filepath="song1.mp3")
    song2 = MusicLibrary(filepath="song2.mp3")
    session.add(song1)
    session.add(song2)
    session.commit()
    
    yield session
    
    session.close()

def test_get_song_id_by_filepath(db_session):
    # Test case 1: Existing song
    file_path = "song1.mp3"
    result = get_song_id_by_filepath(db_session, file_path)
    assert result == 1

    # Test case 2: Non-existing song
    file_path = "nonexistent.mp3"
    result = get_song_id_by_filepath(db_session, file_path)
    assert result is None

    # Test case 3: Another existing song
    file_path = "song2.mp3"
    result = get_song_id_by_filepath(db_session, file_path)
    assert result == 2

def test_get_song_id_by_filepath_with_none_file_path(db_session):
    # Test case: Passing None as file_path
    file_path = None
    result = get_song_id_by_filepath(db_session, file_path)
    assert result is None