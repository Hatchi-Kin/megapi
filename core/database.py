from datetime import datetime

import sqlite3
from sqlalchemy.sql import exists

from core.config import DEFAULT_SETTINGS, SessionLocal
from models.music import MusicLibrary
from models.users import User
from services.auth import hash_password


def get_db():
    """
    Generator that yields a database session and ensures its closure after use.

    Yields:
        SessionLocal: A SQLAlchemy session object for database operations.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def migrate_data_from_sqlite_to_postgres(sqlite_path: str):
    """
    Migrates data from a SQLite database to a PostgreSQL database.

    This function connects to the specified SQLite database, retrieves all records from a specified table,
    and migrates them to the PostgreSQL database if the target table is empty.

    Parameters:
        sqlite_path (str): The file path to the SQLite database.
    """
    # Connect to SQLite database and get the data
    conn_sqlite = sqlite3.connect(sqlite_path)
    sqlite_table_name = "songs"
    cursor = conn_sqlite.cursor()
    cursor.execute(f'SELECT * FROM "{sqlite_table_name}"')
    data = cursor.fetchall()
    columns = [column[0] for column in cursor.description]

    with SessionLocal() as db:
        # Check if any rows exist in the MusicLibrary table in PostgreSQL
        if not db.query(exists().where(MusicLibrary.id != None)).scalar():
            # If not, migrate data from SQLite to PostgreSQL
            for row in data:
                row_dict = dict(zip(columns, row))
                # Replace empty strings with None because PostgreSQL does not allow empty strings for non-string columns
                row_dict = {k: v if v != "" else None for k, v in row_dict.items()}
                # force the id inserted as int
                row_dict["id"] = int(row_dict["id"])
                db.add(MusicLibrary(**row_dict))

            # Commit once at the end
            db.commit()
            print(f"Data successfully migrated from SQLite to PostgreSQL")
        else:
            print(f"Table already exists and is not empty in PostgreSQL")


def create_admin_if_none():
    """
    Checks if an admin user exists in the database, and if not, creates one using default settings.

    This function is useful for initial setup and ensures that there is at least one admin user in the system.
    """
    # Check if any users exist
    with SessionLocal() as db:
        if db.query(User).first() is None:
            # If not, create an admin user
            admin = User(
                id=1,
                email=DEFAULT_SETTINGS.pg_email,
                username=DEFAULT_SETTINGS.pg_user,
                hashed_password=hash_password(DEFAULT_SETTINGS.pg_password),
                registered_at=datetime.now(),
                is_admin=True,
            )
            db.add(admin)
            db.commit()
