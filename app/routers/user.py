from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.models import User
from app.db.deps import get_db
from app.utils.auth import get_current_user
from app.utils.security import hash_password, verify_password
from app.utils.jwt import create_access_token, create_refresh_token
from app.schemas.user import UserRegister, UserLogin, TokenResponse

router = APIRouter(tags=["Users"])

# ----------------------------
# Register User
# ----------------------------

@router.post("/user-register")
def register_user(payload: UserRegister, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == payload.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(
        username=payload.username,
        email=payload.email,
        password=hash_password(payload.password),
        role=payload.role
    )
    db.add(user)
    db.commit()
    return {"message": "User registered successfully"}

# ----------------------------
# Login User
# ----------------------------

@router.post("/user-login", response_model=TokenResponse)
def login_user(payload: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()

    if not user or not verify_password(payload.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = create_access_token({"sub": user.email})
    refresh_token = create_refresh_token({"sub": user.email})

    return {
        "access_token": access_token,
        "refresh_token": refresh_token
    }


# ----------------------------
# Get Current User
# ----------------------------

@router.get("/me")
def read_me(current_user: str = Depends(get_current_user)):
    return {"email": current_user}


