from fastapi_login import LoginManager
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import create_engine
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings, loaded from environment variables."""
    secret_key: str = ""  
    algorithm: str = ""
    access_token_expire_minutes: int = 30
    database_url: str = ""
    postgre_music_table: str = ""
    pg_user: str = ""
    pg_email: str = ""
    pg_password: str = ""
    milvus_uri: str = ""
    milvus_api_key: str = ""


DEFAULT_SETTINGS = Settings(_env_file=".env") 

engine = create_engine(DEFAULT_SETTINGS.database_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
login_manager = LoginManager(DEFAULT_SETTINGS.secret_key, "/auth/token")

Base = declarative_base()


swagger_tags = [
    {
        "name": "users",
        "description": "Operations related to authentication",
    },
    {
        "name": "songs",
        "description": "Operations related to music_library table in postgres database fastapi_db",
    },
    {
        "name": "milvus",
        "description": "Operations related to the vector Database Milvus hosted by zilliz",
    },
    {
        "name": "signup / login", 
        "description": "Mini front-end to test the OAuth2 fonctionnalities"
    },
]




