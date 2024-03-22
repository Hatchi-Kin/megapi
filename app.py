from sqlalchemy.orm import declarative_base
from fastapi import FastAPI
from fastapi_login import LoginManager

from source.data.database import Base
from source.routes.auth import router as auth_router
from source.routes.music_library import router as music_router
from source.dependencies.config import engine


Base = declarative_base()
Base.metadata.create_all(bind=engine)

tags_metadata = [
    {
        "name": "users",
        "description": "Operations related to authentication",
    },
    {
        "name": "songs",
        "description": "Operations related to songs table in postgres database",
    },
    {
        "name": "milvus",
        "description": "Operations related to Milvus",
    },
    {"name": "signup / login", "description": "mini front to test signup and login"},
]

app = FastAPI(
    title="Megapi",
    description="Right now, a simple login system using FastAPI and FastAPI-Login... but just you wait !",
    version="0.1.0",
    openapi_tags=tags_metadata,
)

manager = LoginManager("SECRET", "/auth/token")

app.include_router(auth_router)
app.include_router(music_router)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
