from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.models import User
from app.db.deps import get_db

router = APIRouter(prefix="/users", tags=["Users"])

@router.post("/")
def create_user(email: str, password: str, username: str, role: str, db: Session = Depends(get_db)):
    user = User(
        email=email,
        password=password,
        username=username,
        role=role
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
