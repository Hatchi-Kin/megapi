import os
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from source.models.music import MusicLibrary, Base

@pytest.fixture
def db():
    # Set up a SQLite database in memory
    engine = create_engine('sqlite:///tests/test.db')
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()

    Base.metadata.create_all(bind=engine)
    yield db

    # Delete the records in the table
    db.query(MusicLibrary).delete()
    db.commit()
    # Remove the database file
    if os.path.isfile("tests/test.db"):
        os.remove("tests/test.db")


def test_add_user(db):
    # Add a record to the table
    new_song = MusicLibrary(
        id=1,
        filename="test_filename",
        filepath="test_filepath",
        album_folder="test_album_folder",
        artist_folder="test_artist_folder",
        filesize=123.0,
        title="test_title",
        artist="test_artist",
        album="test_album",
        year=2021,
        tracknumber=6,
        genre="test_genre",
        top_5_genres="['test_genre1', 'test_genre2']",
    )
    db.add(new_song)
    db.commit()

    # Verify that the record was added
    assert db.query(MusicLibrary).count() == 1, "Record was not added to the database"

    # Verify that the database file exists
    assert os.path.isfile("tests/test.db"), "Database file does not exist"
