from fastapi import APIRouter, Depends

from core.config import login_manager
from services.monitoring import get_all_pi_stats

router = APIRouter(prefix="/monitoring")


@router.get("/pi", tags=["monitoring"])
async def get_all_pi(user=Depends(login_manager)):
    """Get all the monitoring stats of the Raspberry Pi."""
    return get_all_pi_stats()
    