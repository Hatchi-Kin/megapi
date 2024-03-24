from fastapi_login import LoginManager
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import create_engine
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    secret: str = ""  # automatically taken from environment variable
    database_url: str = ""
    postgre_music_table: str = "music_library"
    milvus_uri: str = ""
    milvus_api_key: str = ""



DEFAULT_SETTINGS = Settings(_env_file=".env")

engine = create_engine(DEFAULT_SETTINGS.database_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
manager = LoginManager(DEFAULT_SETTINGS.secret, "/auth/token")

Base = declarative_base()