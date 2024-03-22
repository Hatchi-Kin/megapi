from sqlalchemy import create_engine, text

def list_postgres_tables(postgres_url):
    engine_postgres = create_engine(postgres_url)
    with engine_postgres.connect() as connection:
        result = connection.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"))
        for row in result:
            print("Table:", row[0])  # Access the first element of the tuple


def print_first_3_rows(postgres_url, table_name):
    engine_postgres = create_engine(postgres_url)
    with engine_postgres.connect() as connection:
        result = connection.execute(text(f"SELECT * FROM {table_name} LIMIT 3"))
        print(f"Fetching rows from {table_name}...")
        rows_fetched = 0
        for row in result:
            print(row)
            rows_fetched += 1
        print(f"Fetched {rows_fetched} rows from {table_name}")
        
# Call the function
# list_postgres_tables('postgresql://admin:example@localhost:5432/fastapi_db')
print_first_3_rows('postgresql://admin:example@localhost:5432/fastapi_db', 'music_library')