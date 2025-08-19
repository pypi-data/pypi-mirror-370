from pydantic import BaseModel, ConfigDict, Field


class ResourceSpec(BaseModel):
    cpu: str | None = None
    memory: str | None = None
    gpu: str | None = Field(default=None, alias="nvidia.com/gpu")

    model_config = ConfigDict(populate_by_name=True)


class Resources(BaseModel):
    Requests: ResourceSpec | None = None
    Limits: ResourceSpec | None = None
