from pathlib import Path

from ..base import InferenceServiceProperties
from .types import PlatformType


class TritonserverProperties(InferenceServiceProperties):
    MaxBatchSize: int
    ModelRepositoryUri: Path | None = None
    Platform: PlatformType

    def __setattr__(self, name, value):
        if name == "Platform":
            raise AttributeError("Platform is a constant and cannot be changed.")
        super().__setattr__(name, value)
