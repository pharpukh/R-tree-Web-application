from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.user.models import User
from app.user.schemas import UserCreate
from app.config import get_password_hash


async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    """
    Queries the database for a user with the given email.
    Returns the first user found or None if no such user exists.
    """
    result = await db.execute(select(User).where(User.email == email))
    return result.scalars().first()


async def create_user(db: AsyncSession, user_in: UserCreate) -> User:
    """
    Creates a new user in the database.
    The password is hashed before saving.
    """
    hashed_pw = get_password_hash(user_in.password)
    db_user = User(email=user_in.email, hashed_password=hashed_pw)
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user
