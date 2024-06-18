from fastapi_login import LoginManager
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import create_engine
from pydantic_settings import BaseSettings
from minio import Minio
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

# Application settings, loaded from environment variables
class Settings(BaseSettings):
    """Application settings, loaded from environment variables."""
    secret_key: str = ""  
    algorithm: str = ""
    access_token_expire_minutes: int = 180
    database_url: str = ""
    postgre_music_table: str = ""
    pg_user: str = ""
    pg_email: str = ""
    pg_password: str = ""
    milvus_uri: str = ""
    milvus_api_key: str = ""
    milvus_512_collection_name: str = ""
    milvus_87_collection_name: str = ""
    minio_root_user: str = ""
    minio_bucket_name: str = ""
    minio_temp_bucket_name: str = ""
    minio_openl3_bucket_name: str = ""
    minio_openl3_file_name: str = ""
    minio_root_password: str = ""
    minio_endpoint: str ="",
    minio_access_key: str = "",
    minio_secret_key: str =""
    spotify_client_id: str = "",
    spotify_client_secret: str = "",
    cyanite_token: str = ""

    model_config = {
        "env_file": ".env",
        "extra": "allow"  # allow extra fields
    }


DEFAULT_SETTINGS = Settings(_env_file=".env") 

# SQLAlchemy engine, sessionmaker and Base for interacting with the database
engine = create_engine(DEFAULT_SETTINGS.database_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# FastAPI-Login manager for handling authentication
login_manager = LoginManager(DEFAULT_SETTINGS.secret_key, "/auth/token")

# Minio client for self hosted object storage
minio_client = Minio(
    endpoint=DEFAULT_SETTINGS.minio_endpoint,
    access_key=DEFAULT_SETTINGS.minio_access_key,
    secret_key=DEFAULT_SETTINGS.minio_secret_key,
    secure=True # True if you are using https, False if http
)

# Spotipy client for metadata from Spotify API 
spotify_client_credentials_manager = SpotifyClientCredentials(
    client_id=DEFAULT_SETTINGS.spotify_client_id,
    client_secret=DEFAULT_SETTINGS.spotify_client_secret
)
sp= spotipy.Spotify(client_credentials_manager=spotify_client_credentials_manager)


# List of tags for the Swagger UI / auto-generated documentation
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
        "name": "favorites",
        "description": "Operations related to the users favorites",
    },
    {
        "name": "user_uploads",
        "description": "Operations related to the user_uploads table in postgres database fastapi_db",
    },
    {
        "name": "OpenL3",
        "description": "Operations related to the OpenL3 embeddings extractor model"
    },
    {
        "name": "milvus",
        "description": "Operations related to the vector Database Milvus hosted by zilliz",
    },
    {
        "name": "auth gui", 
        "description": "Mini front-end to test the OAuth2 fonctionnalities"
    },
    {
        "name": "MinIO",
        "description": "Operations related to the MinIO Object Storage"
    },
    {
        "name": "lyrics",
        "description": "Operations related to the lyrics.ovh API: https://lyricsovh.docs.apiary.io/"
    }, 
    {
        "name": "spotinite",
        "description": "Operations leveraging spotipy and the cyanite API - https://cyanite.ai/docs/."
    },
    {
        "name": "monitoring",
        "description": "Operations related to the monitoring different metrics of the globals solution."
    },
]

