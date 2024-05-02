from fastapi import APIRouter, Depends, HTTPException

from core.config import login_manager
from services.pi_monitoring import get_pi_cpu_temperature, get_pi_cpu_usage, get_pi_memory_usage, get_pi_disk_usage, get_all_pi_stats


router = APIRouter(prefix="/pi_monitoring")


@router.get("/temp", tags=["Pi Monitoring"])
async def get_pi_temp(user=Depends(login_manager)):
    """Get the CPU temperature of the Raspberry Pi."""
    return get_pi_cpu_temperature()


@router.get("/cpu", tags=["Pi Monitoring"])
async def get_pi_cpu(user=Depends(login_manager)):
    """Get the CPU usage of the Raspberry Pi."""
    return get_pi_cpu_usage()


@router.get("/memory", tags=["Pi Monitoring"])
async def get_pi_memory(user=Depends(login_manager)):
    """Get the memory usage of the Raspberry Pi."""
    return get_pi_memory_usage()


@router.get("/disk", tags=["Pi Monitoring"])
async def get_pi_disk(user=Depends(login_manager)):
    """Get the disk usage of the Raspberry Pi."""
    return get_pi_disk_usage()


@router.get("/all", tags=["Pi Monitoring"])
async def get_all_pi(user=Depends(login_manager)):
    """Get all the monitoring stats of the Raspberry Pi."""
    return get_all_pi_stats()
    



