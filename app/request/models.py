from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as pgUUID
from datetime import datetime
from app.db import Base
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.types import LargeBinary


# UserRequest model: represents a query/request for building an R-tree by a user.
class UserRequest(Base):
    # Primary key for the request (integer type)
    id = Column(Integer, primary_key=True, index=True)
    # Foreign key linking to the user's UUID in the users table.
    user_id = Column(pgUUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    # Number of objects to generate/build the R-tree.
    number_of_objects = Column(Integer, nullable=False)
    # Dimensionality of the objects/space.
    dimensions = Column(Integer, nullable=False)
    # Maximum number of entries per node in the R-tree.
    max_entries = Column(Integer, nullable=False)
    # The split method used in R-tree (either 'quadratic' or 'linear').
    split_method = Column(String, nullable=False)

    # The minimum coordinates for the main region where objects are generated.
    main_region_min_coordinates = Column(JSONB, nullable=False)
    # The maximum coordinates for the main region.
    main_region_max_coordinates = Column(JSONB, nullable=False)

    # The serialized (pickled) R-tree data.
    r_tree_data = Column(LargeBinary, nullable=True)

    # Timestamp when the request was created. Defaults to the current UTC time.
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationship to the User model.
    user = relationship("User", back_populates="requests")
