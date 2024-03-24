from fastapi import FastAPI

from source.routes.auth import router as auth_router
from source.routes.music_library import router as music_router
from source.routes.milvus import router as milvus_router
from source.settings.config import Base, engine


Base.metadata.create_all(bind=engine)

tags_metadata = [
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

app = FastAPI(
    title="Megapi",
    description="Right now, a simple login system using FastAPI and FastAPI-Login... but just you wait !",
    version="0.1.0",
    openapi_tags=tags_metadata,
)

app.include_router(auth_router)
app.include_router(music_router)
app.include_router(milvus_router)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
