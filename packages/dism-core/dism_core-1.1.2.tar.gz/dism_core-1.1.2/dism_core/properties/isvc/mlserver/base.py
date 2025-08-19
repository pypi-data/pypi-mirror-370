from pathlib import Path

from ..base import InferenceServiceProperties


class MLServerProperties(InferenceServiceProperties):
    CodeUri: Path
    Handler: str
    ModelUri: Path
