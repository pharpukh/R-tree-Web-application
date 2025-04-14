from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import jwt
from sqlalchemy.ext.asyncio import AsyncSession
from app.user import crud
from app.db import db_helper

# Define an OAuth2 scheme to extract the token from the Authorization header.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/login")

# Secret key and algorithm for JWT decoding.
SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"


async def get_current_user(token: str = Depends(oauth2_scheme),
                           db: AsyncSession = Depends(db_helper.scoped_session_dependency)):
    """
    Dependency that extracts the current user based on the provided JWT token.
    It decodes the token, retrieves the email from its payload, and fetches the user from the database.
    Raises HTTP 401 if the token is invalid or user not found.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials"
            )
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )
    user = await crud.get_user_by_email(db, email)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user
