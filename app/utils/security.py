from passlib.context import CryptContext
from app.core import config

# ===============================
# Password hashing context
# ===============================
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=config.BCRYPT_ROUNDS
)


# ===============================
# Utility functions
# ===============================
def hash_password(password: str) -> str:
    """
    Hash a plain text password.
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain password against a hashed password.
    """
    return pwd_context.verify(plain_password, hashed_password)
