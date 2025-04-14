from sqlalchemy import Column, String, DateTime
from datetime import datetime
from app.db import Base
from sqlalchemy.orm import relationship


# User model representing a user in the system.
class User(Base):
    # Email field: unique, indexed and cannot be null.
    email = Column(String, unique=True, index=True, nullable=False)
    # Hashed password stored as string.
    hashed_password = Column(String, nullable=False)
    # Date and time when the user was created. Defaults to the current UTC time.
    created_at = Column(DateTime, default=datetime.utcnow)
    # Relationship to UserRequest objects.
    # Cascade delete ensures that all requests associated with a user are deleted when the user is deleted.
    requests = relationship("UserRequest", back_populates="user", cascade="all, delete")
