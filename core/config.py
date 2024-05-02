from fastapi_login import LoginManager
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import create_engine
from pydantic_settings import BaseSettings
from minio import Minio
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials


class Settings(BaseSettings):
    """Application settings, loaded from environment variables."""
    secret_key: str = ""  
    algorithm: str = ""
    access_token_expire_minutes: int = 60
    database_url: str = ""
    postgre_music_table: str = ""
    pg_user: str = ""
    pg_email: str = ""
    pg_password: str = ""
    milvus_uri: str = ""
    milvus_api_key: str = ""
    milvus_collection_name: str = ""
    minio_root_user: str = ""
    minio_bucket_name: str = ""
    minio_root_password: str = ""
    minio_endpoint: str ="",
    minio_access_key: str = "",
    minio_secret_key: str =""
    spotify_client_id: str = "",
    spotify_client_secret: str = "",
    cyanite_token: str = ""

    class Config:
        env_file = ".env"
        extra = "allow"  # allow extra fields


DEFAULT_SETTINGS = Settings(_env_file=".env") 

engine = create_engine(DEFAULT_SETTINGS.database_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
login_manager = LoginManager(DEFAULT_SETTINGS.secret_key, "/auth/token")
Base = declarative_base()

minio_client = Minio(
    endpoint=DEFAULT_SETTINGS.minio_endpoint,
    access_key=DEFAULT_SETTINGS.minio_access_key,
    secret_key=DEFAULT_SETTINGS.minio_secret_key,
    secure=False # True if you are using https, False if http
)

# Set up Spotipy with your Spotify client credentials
spotify_client_credentials_manager = SpotifyClientCredentials(
    client_id=DEFAULT_SETTINGS.spotify_client_id,
    client_secret=DEFAULT_SETTINGS.spotify_client_secret
)
sp= spotipy.Spotify(client_credentials_manager=spotify_client_credentials_manager)



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
        "name": "auth gui", 
        "description": "Mini front-end to test the OAuth2 fonctionnalities"
    },
    {
        "name": "miniO",
        "description": "Operations related to the minio database"
    },
    {
        "name": "lyrics",
        "description": "Operations related to the lyrics.ovh API: https://lyricsovh.docs.apiary.io/"
    }, 
    {
        "name": "spotinite",
        "description": "Operations related to the spotinite API: https://cyanite.ai/docs/ leveraging spotipy and the cyanite API."
    },
    {
        "name": "Pi Monitoring",
        "description": "Operations related to the monitoring of the Raspberry Pi"
    },
    {
        "name": "Prometheus Metrics",
        "description": "Operations related to the monitoring of the FastAPI application"
    }
]





