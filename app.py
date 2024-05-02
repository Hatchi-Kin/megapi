from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from prometheus_fastapi_instrumentator import Instrumentator
from prometheus_client import Gauge, generate_latest

from routes.auth import router as auth_router
from routes.music import router as music_router
from routes.milvus import router as milvus_router
from routes.minio import router as minio_router
from routes.lyrics import router as lyrics_router
from routes.spotinite import router as spotinite_router
from routes.pi_monitoring import router as pi_monitoring_router
from core.config import Base, engine, swagger_tags
from core.database import migrate_data_from_sqlite_to_postgres, create_admin_if_none
from services.pi_monitoring import get_pi_cpu_temperature, get_pi_cpu_usage, get_pi_memory_usage
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

# Create a Gauge object for each metric we want to expose to Prometheus
cpu_temp_gauge = Gauge('cpu_temperature', 'CPU Temperature')
cpu_usage_gauge = Gauge('cpu_usage', 'CPU Usage')
memory_usage_gauge = Gauge('memory_usage', 'Memory Usage')

@app.get("/metrics", include_in_schema=True, tags=["Prometheus Metrics"])
async def metrics():
    cpu_temp_gauge.set(get_pi_cpu_temperature())
    cpu_usage_gauge.set(get_pi_cpu_usage())
    memory_usage_gauge.set(get_pi_memory_usage())
    metrics_page = generate_latest()
    return app.dependency_overrides[app.router.routes[-1].endpoint]()


app.include_router(auth_router)
app.include_router(music_router)
app.include_router(milvus_router)
app.include_router(minio_router)
app.include_router(lyrics_router)
app.include_router(spotinite_router)
app.include_router(pi_monitoring_router)


Base.metadata.create_all(bind=engine)
migrate_data_from_sqlite_to_postgres("core/data/music.db")
create_admin_if_none()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)