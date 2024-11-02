from typing import List

from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import func
from models.music import MusicLibrary


def get_n_random_examples_of_specified_genre(db: Session, genre: str, num_examples: int) -> List[MusicLibrary]:
    """
    Get a random selection of rows that have the specified genre.

    :param db: SQLAlchemy Session object
    :param genre: str - The genre to filter by
    :param num_examples: int - The number of examples wanted
    :return: List of rows with the specified genre
    """
    try:
        # Count the total number of rows with the specified genre
        total_rows = db.query(MusicLibrary).filter(MusicLibrary.genre == genre).count()

        # If the number of rows is less than or equal to the requested number, return all rows
        if total_rows <= num_examples:
            return db.query(MusicLibrary).filter(MusicLibrary.genre == genre).all()

        # Otherwise, return a random selection of the requested number of rows
        return db.query(MusicLibrary).filter(MusicLibrary.genre == genre).order_by(func.random()).limit(num_examples).all()
    except Exception as e:
        print(f"Error fetching random examples: {e}")
        return []

