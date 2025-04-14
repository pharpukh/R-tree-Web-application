from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from app.user import crud
from app.user import schemas
from app.db import db_helper
from app.config import verify_password, create_access_token
from datetime import timedelta
from app.user.schemas import Token

router = APIRouter()

# Define token expiration time (in minutes)
ACCESS_TOKEN_EXPIRE_MINUTES = 30
SECRET_KEY = "your-secret-key"


@router.post("/register", response_model=schemas.UserOut)
async def register_user(user_in: schemas.UserCreate, db: AsyncSession = Depends(db_helper.scoped_session_dependency)):
    """
    Endpoint to register a new user.
    If the email is already registered, it returns a 400 error.
    """
    db_user = await crud.get_user_by_email(db, user_in.email)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    new_user = await crud.create_user(db, user_in)
    return new_user


@router.post("/login", response_model=Token)
async def login(
        form_data: OAuth2PasswordRequestForm = Depends(),
        db: AsyncSession = Depends(db_helper.scoped_session_dependency)
):
    """
    Endpoint to authenticate a user.
    It verifies the user's credentials and returns a JWT token if successful.
    """
    db_user = await crud.get_user_by_email(db, form_data.username)
    if not db_user or not verify_password(form_data.password, db_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": db_user.email, "user_id": str(db_user.id)},
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}
