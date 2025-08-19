import re
from typing import Annotated

from pydantic import BaseModel, StringConstraints, field_validator


class Tag(BaseModel):
    Name: Annotated[
        str, StringConstraints(max_length=63)
    ]  # There are not hard restrictions for this, but let's keep things standardized
    Value: str

    @field_validator("Name")
    @classmethod
    def validate_name_chars(cls, v):
        if not re.fullmatch(r"^[a-z0-9\-_]+$", v):
            raise ValueError("String must contain only lowercase alphanumeric characters, hyphens, or underscores")
        return v


class BaseProperties(BaseModel):
    Description: str
    Name: Annotated[
        str, StringConstraints(max_length=36)
    ]  # The final service name has to be limited to 63 characters, it will be a composed string: {stage:5}-{workspace:18}-{Name:36}-{version:4}
    Tags: list[Tag] | None = None

    @field_validator("Name")
    @classmethod
    def validate_name_chars(cls, v):
        pattern = r"^[a-z0-9]([-a-z0-9]*[a-z0-9])?(\.[a-z0-9]([-a-z0-9]*[a-z0-9])?)*$"
        if not re.fullmatch(pattern, v):
            raise ValueError(f"String violates RFC 1123 subdomain naming conventions. Validation is done by {pattern}")
        return v
