from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from prometheus_client import generate_latest

from core.config import login_manager
from services.monitoring import get_all_pi_stats, create_and_set_pi_gauges

router = APIRouter(prefix="/monitoring")


@router.get("/pi", tags=["monitoring"])
async def get_all_pi(user=Depends(login_manager)):
    """Get all the monitoring stats of the Raspberry Pi."""
    return get_all_pi_stats()
    

@router.get("/metrics", include_in_schema=False, tags=["Prometheus Metrics"])
async def metrics():
    create_and_set_pi_gauges()
    metrics_page = generate_latest()
    return Response(metrics_page, media_type="text/plain")

