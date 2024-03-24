import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from source.models.music import MusicLibrary, Base


class TestMusicLibrary:
    def setup_method(self, method):
        # Set up a SQLite database in memory
        self.engine = create_engine("sqlite:///tests/test.db")
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        self.db = SessionLocal()

        # Create the tables
        Base.metadata.create_all(bind=self.engine)

    def teardown_method(self, method):
        # Delete the records in the table
        self.db.query(MusicLibrary).delete()
        self.db.commit()

        # Remove the database file
        if os.path.isfile("tests/test.db"):
            os.remove("tests/test.db")

    def test_add_user(self):
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
        self.db.add(new_song)
        self.db.commit()

        # Verify that the record was added
        assert self.db.query(MusicLibrary).count() == 1

        # Verify that the database file exists
        assert os.path.isfile("tests/test.db") == True
