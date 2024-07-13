from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from core.database import get_db
from core.config import login_manager
from services.uploaded import get_user_uploads


router = APIRouter(prefix="/uploaded")


@router.get("/", tags=["user_uploads"])
async def get_user_list_of_uploads(user=Depends(login_manager), db: Session = Depends(get_db)):
    return get_user_uploads(db, user.id)