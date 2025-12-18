from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.deps import get_db
from app.schemas.user_details import UserDetailsOut
from app.services.user_details_service import get_user_details

router = APIRouter(
    prefix="/user-details",
    tags=["User Details"]
)

@router.get("/", response_model=list[UserDetailsOut])
def user_details(db: Session = Depends(get_db)):
    return get_user_details(db)

