from sqlalchemy import create_engine, text
import sqlite3

def migrate_data_from_sqlite_to_postgres(sqlite_path, postgres_url, table_name):
    # Create engine for PostgreSQL
    engine_postgres = create_engine(postgres_url)

    # Connect to SQLite database
    conn_sqlite = sqlite3.connect(sqlite_path)
    sqlite_table_name = "songs"

    # Get data from SQLite database
    cursor = conn_sqlite.cursor()
    cursor.execute(f'SELECT * FROM "{sqlite_table_name}"')
    data = cursor.fetchall()
    columns = [column[0] for column in cursor.description]

    with engine_postgres.begin() as connection:  # Use a transaction
        # Check if table exists in PostgreSQL
        if not engine_postgres.dialect.has_table(connection, table_name):
            print(f"Table {table_name} does not exist in PostgreSQL")
            return

        # Insert data into PostgreSQL
        for row in data:
            # Create a dictionary that maps column names to values
            row_dict = dict(zip(columns, row))
            # Replace empty strings with None
            row_dict = {k: v if v != "" else None for k, v in row_dict.items()}
            # Construct the SQL statement
            sql = text(f"INSERT INTO {table_name} ({', '.join(row_dict.keys())}) VALUES ({', '.join(':' + key for key in row_dict.keys())})")
            # Execute the SQL statement with the row data
            connection.execute(sql, row_dict)  # Pass the row data as a dictionary

    print(f"Data successfully migrated from SQLite to PostgreSQL")

# Call the function
migrate_data_from_sqlite_to_postgres('music.db', 'postgresql://admin:example@localhost:5432/fastapi_db', 'music_library')