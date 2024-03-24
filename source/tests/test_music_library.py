import os
import pytest
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.orm import declarative_base, sessionmaker

metadata = MetaData()

Base = declarative_base()

engine = create_engine(
    f"postgresql://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}@{os.getenv('POSTGRES_HOST')}:{os.getenv('POSTGRES_PORT')}/test_db"
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class MusicTest(Base):
    __tablename__ = "test_music_library"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String)
    filepath = Column(String)
    album_folder = Column(String)
    artist_folder = Column(String)
    filesize = Column(Float)
    title = Column(String)
    artist = Column(String)
    album = Column(String)
    year = Column(Integer)
    tracknumber = Column(Integer)
    genre = Column(String)
    top_5_genres = Column(String)

metadata.create_all(engine)

def test_add_row():

    db = SessionLocal()
    try:
        # Add a row to the music_library table
        db.add(
            MusicTest(
                id=1,
                filename="test",
                filepath="test",
                album_folder="test",
                artist_folder="test",
                filesize=1.0,
                title="test",
                artist="test",
                album="test",
                year=2000,
                tracknumber=1,
                genre="test",
                top_5_genres="test",
            )
        )
        db.commit()
        row = db.query(MusicTest).get(1)
        assert row is not None
        assert row.filename == "test"
        print(row)
    finally:
        db.close()


def test_delete_row():
    db = SessionLocal()
    try:
        # Delete the row we added in the previous test
        row = db.query(MusicTest).get(1)
        db.delete(row)
        db.commit()
        row = db.query(MusicTest).get(1)
        print(row)
        assert row is None
    finally:
        db.close()
