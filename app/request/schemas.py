from pydantic import BaseModel, field_validator, model_validator, conint
from typing import List, Literal, Optional
from datetime import datetime
import json


# Schema for creating a new R-tree request.
class RequestCreate(BaseModel):
    number_of_objects: conint(gt=0)
    dimensions: conint(gt=1)
    max_entries: conint(ge=2)
    split_method: Literal["quadratic", "linear"]
    main_region_min_coordinates: List[float]
    main_region_max_coordinates: List[float]

    # Validator to ensure the number of coordinates matches the specified dimensions.
    @field_validator("main_region_min_coordinates", "main_region_max_coordinates", mode="before")
    def validate_coordinates_length(cls, value, info):
        dimensions = info.data.get("dimensions")
        if dimensions is None:
            raise ValueError("Dimensions must be specified before coordinates.")
        if len(value) != dimensions:
            raise ValueError(
                f"Coordinates length mismatch. Expected {dimensions} numbers but got {len(value)}."
            )
        return value

    # Model-level validator to ensure each maximum coordinate is greater than the corresponding minimum.
    @model_validator(mode="after")
    def check_coordinates(cls, model: "RequestCreate") -> "RequestCreate":
        for i, (min_val, max_val) in enumerate(
                zip(model.main_region_min_coordinates, model.main_region_max_coordinates)):
            if max_val <= min_val:
                raise ValueError(
                    f"Maximum coordinate at index {i} ({max_val}) must be greater than minimum coordinate ({min_val})."
                )
        return model


# Schema for basic output of a request.
class RequestOut(BaseModel):
    id: int
    number_of_objects: conint(gt=0)
    dimensions: conint(gt=1)
    max_entries: conint(ge=2)
    split_method: Literal["quadratic", "linear"]
    main_region_min_coordinates: List[float]
    main_region_max_coordinates: List[float]
    created_at: datetime

    # Validator to parse coordinates from a JSON string if needed.
    @field_validator("main_region_min_coordinates", "main_region_max_coordinates", mode="before")
    def parse_coordinates(cls, value):
        if isinstance(value, str):
            try:
                return json.loads(value)
            except Exception as e:
                raise ValueError(f"Could not parse JSON: {e}")
        return value

    class Config:
        # Allow constructing the model from ORM objects.
        from_attributes = True


# Extended output schema including an optional base64-encoded image.
class RequestOutFull(RequestOut):
    image_base64: Optional[str] = None
