import sqlite3
from source.settings.config import SessionLocal
from source.models.music import MusicLibrary


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
        # Drop the table if it exists
        table_exists = db.query(MusicLibrary).first()
        if table_exists:
            db.query(MusicLibrary).delete()
            db.commit()
            print(f"Table {table_name} dropped in PostgreSQL")
        # Insert data into PostgreSQL
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