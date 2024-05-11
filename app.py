from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from prometheus_fastapi_instrumentator import Instrumentator

from routes.auth import router as auth_router
from routes.music import router as music_router
from routes.favorites import router as playlist_router
from routes.milvus import router as milvus_router
from routes.minio import router as minio_router
from routes.lyrics import router as lyrics_router
from routes.spotinite import router as spotinite_router
from routes.monitoring import router as monitoring_router
from core.config import Base, engine, swagger_tags
from core.database import migrate_data_from_sqlite_to_postgres, create_admin_if_none


app = FastAPI(
    title="Megapi",
    description="Right now, a simple login system using FastAPI and FastAPI-Login... but just you wait !",
    version="0.1.0",
    openapi_tags=swagger_tags,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],  
)

Instrumentator().instrument(app).expose(app)


app.include_router(auth_router)
app.include_router(music_router)
app.include_router(playlist_router)
app.include_router(milvus_router)
app.include_router(minio_router)
app.include_router(lyrics_router)
app.include_router(spotinite_router)
app.include_router(monitoring_router)


Base.metadata.create_all(bind=engine)
migrate_data_from_sqlite_to_postgres("core/data/music.db")
create_admin_if_none()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)