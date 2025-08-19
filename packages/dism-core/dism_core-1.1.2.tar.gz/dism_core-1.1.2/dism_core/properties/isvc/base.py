from ..base import BaseProperties
from .resources import Resources as ResourcesModel
from .signature import InputSignature, OutputSignature


class InferenceServiceProperties(BaseProperties):
    AnomalyThreshold: float | None = None
    BuiltinThreshold: bool | None = None
    FlaggingKey: str | None = None
    InputSignature: list[InputSignature]
    MetricKey: str
    OutputSignature: list[OutputSignature]
    Image: str | None = None
    Resources: ResourcesModel | None = None
