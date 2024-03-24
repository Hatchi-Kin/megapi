import sqlite3
from sqlalchemy.orm import Session
from passlib.context import CryptContext

from source.settings.config import SessionLocal, DEFAULT_SETTINGS
from source.models.music import MusicLibrary
from source.models.users import User


from sqlalchemy.sql import exists

def migrate_data_from_sqlite_to_postgres(sqlite_path, table_name):
    # Connect to SQLite database
    conn_sqlite = sqlite3.connect(sqlite_path)
    sqlite_table_name = "songs"

    # Get data from SQLite database
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
            print(f"Table {table_name} already exists and is not empty in PostgreSQL")


def create_admin_if_none(engine):
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    with Session(engine) as db:
        # Check if any users exist
        if db.query(User).first() is None:
            # If not, create an admin user
            admin = User(
                id=1,
                email=DEFAULT_SETTINGS.pg_user,
                hashed_password=pwd_context.hash(DEFAULT_SETTINGS.pg_password),
            )
            db.add(admin)
            db.commit()
