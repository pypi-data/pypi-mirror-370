from pathlib import Path

from .base import TritonserverProperties
from .types import PlatformType


class TorchscriptProperties(TritonserverProperties):
    ModelUri: Path
    Platform: PlatformType = PlatformType.TORCHSCRIPT
