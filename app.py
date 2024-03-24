from fastapi import FastAPI

from source.routes.auth import router as auth_router
from source.routes.music_library import router as music_router
from source.routes.milvus import router as milvus_router
from source.settings.config import Base, engine, tags_metadata


Base.metadata.create_all(bind=engine)

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
