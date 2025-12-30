from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError

from app.core import config


# ===============================
# OAuth2 scheme
# ===============================
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="user-login")


# ===============================
# Auth dependency
# ===============================
def get_current_user(token: str = Depends(oauth2_scheme)) -> str:
    """
    Extract and validate JWT token.
    Returns the user's email (subject) if valid.
    """
    try:
        payload = jwt.decode(
            token,
            config.SECRET_KEY,
            algorithms=[config.JWT_ALGORITHM]
        )

        email: str | None = payload.get("sub")
        if email is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials"
            )

        return email

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
