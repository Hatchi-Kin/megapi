from fastapi import APIRouter, Depends

from core.config import login_manager
from services.monitoring import get_all_pi_stats

router = APIRouter(prefix="/monitoring")


@router.get("/pi", tags=["monitoring"])
async def get_all_pi(user=Depends(login_manager)):
    """
    Retrieves comprehensive monitoring statistics for a Linux host machine.

    These statistics include CPU usage, memory usage, disk space, temperature readings.

    - **user**: User - The authenticated user making the request, verified through the `login_manager`.
    - **return**: A JSON response containing the linux host's monitoring statistics.
    """
    return get_all_pi_stats()
    