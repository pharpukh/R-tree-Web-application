from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Dict
import jwt

# Create a CryptContext instance to handle password hashing with bcrypt.
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    """
    Returns a hashed password using bcrypt.
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifies a plain password against a given hashed password.
    """
    return pwd_context.verify(plain_password, hashed_password)


# Secret key and settings for JWT (JSON Web Tokens).
SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def create_access_token(data: Dict[str, str], expires_delta: timedelta = None) -> str:
    """
    Creates a JWT access token containing the provided data.
    If expires_delta is not provided, a default expiry time is used.
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta if expires_delta else timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
