from datetime import datetime, timedelta
from jose import jwt

from app.core import config


def create_access_token(data: dict) -> str:
    """
    Create a JWT access token.

    Args:
        data (dict): Payload data (must include 'sub')

    Returns:
        str: Encoded JWT access token
    """
    to_encode = data.copy()

    expire = datetime.utcnow() + timedelta(
        minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES
    )

    to_encode.update({"exp": expire})

    return jwt.encode(
        to_encode,
        config.SECRET_KEY,
        algorithm=config.JWT_ALGORITHM
    )


def create_refresh_token(data: dict) -> str:
    """
    Create a JWT refresh token.

    Args:
        data (dict): Payload data (must include 'sub')

    Returns:
        str: Encoded JWT refresh token
    """
    to_encode = data.copy()

    expire = datetime.utcnow() + timedelta(
        days=config.REFRESH_TOKEN_EXPIRE_DAYS
    )

    to_encode.update({"exp": expire})

    return jwt.encode(
        to_encode,
        config.SECRET_KEY,
        algorithm=config.JWT_ALGORITHM
    )
