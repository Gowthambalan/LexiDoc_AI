from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.deps import get_db
from app.services.recent_response_service import get_recent_responses
from app.schemas.recent_response import RecentResponseOut

router = APIRouter(prefix="/recent-responses", tags=["Recent Responses"])

@router.get("/", response_model=list[RecentResponseOut])
def recent_responses(db: Session = Depends(get_db)):
    return get_recent_responses(db)
