from uuid import uuid4, UUID
from sqlalchemy.orm import DeclarativeBase, declared_attr, Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID as pgUUID


class Base(DeclarativeBase):
    __abstract__ = True

    @declared_attr
    def __tablename__(cls) -> str:
        # Automatically generate a table name by converting the class name to lowercase and adding an "s"
        return f"{cls.__name__.lower()}s"

    # Define an id column using UUID as primary key with automatic generation using uuid4
    id: Mapped[UUID] = mapped_column(pgUUID(as_uuid=True), primary_key=True, default=uuid4)
