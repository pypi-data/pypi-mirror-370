from pathlib import Path

from .base import TritonserverProperties
from .types import PlatformType


class TensorflowSavedModelProperties(TritonserverProperties):
    SavedModelUri: Path
    Platform: PlatformType = PlatformType.TENSORFLOW_SAVEDMODEL
