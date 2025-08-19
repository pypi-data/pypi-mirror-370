from pathlib import Path

from .base import TritonserverProperties
from .types import PlatformType


class ONNXProperties(TritonserverProperties):
    ModelUri: Path
    Platform: PlatformType = PlatformType.ONNX
