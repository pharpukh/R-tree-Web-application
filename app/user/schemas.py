from pydantic import BaseModel, EmailStr
from datetime import datetime


# Schema for user creation: expects a valid email and a plain password.
class UserCreate(BaseModel):
    email: EmailStr
    password: str


# Schema for user login: expects a valid email and a plain password.
class UserLogin(BaseModel):
    email: EmailStr
    password: str


# Schema for outputting user data.
class UserOut(BaseModel):
    email: EmailStr
    created_at: datetime

    class Config:
        # Allows Pydantic to create a model from ORM objects.
        from_attributes = True


# Schema for JWT token response.
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
