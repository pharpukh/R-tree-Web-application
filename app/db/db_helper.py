from asyncio import current_task
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    async_scoped_session,
    AsyncSession,
)
from .session import settings
from sqlalchemy.orm import sessionmaker


class DataBaseHelper:
    """
    A helper class for creating and managing an asynchronous database engine and sessions.
    """

    def __init__(self, url: str, echo: bool = False):
        # Create an async engine using the provided database URL and echo setting.
        self.engine = create_async_engine(
            url=url,
            echo=echo,
        )
        # Create a session factory with specified parameters.
        self.session_factory = async_sessionmaker(
            bind=self.engine,
            autoflush=False,
            autocommit=False,
            expire_on_commit=False,
        )

    def get_scoped_session(self):
        # Create a scoped session that ties the session to the current async task.
        session = async_scoped_session(
            session_factory=self.session_factory, scopefunc=current_task
        )
        return session

    async def session_dependency(self) -> AsyncSession:
        # Provides a dependency that yields a new session, then closes it.
        async with self.session_factory() as session:
            yield session
            await session.close()

    async def scoped_session_dependency(self) -> AsyncSession:
        # Provides a dependency that yields a scoped session, then closes it.
        session = self.get_scoped_session()
        yield session
        await session.close()


# Create a global instance of DataBaseHelper using settings from session.py.
db_helper = DataBaseHelper(
    url=settings.db_url,
    echo=settings.db_echo,
)

print("Using DB URL:", settings.db_url)
