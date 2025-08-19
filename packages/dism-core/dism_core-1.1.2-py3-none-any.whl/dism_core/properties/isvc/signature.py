from enum import Enum

from pydantic import BaseModel


class DataTypeEnum(str, Enum):
    BOOL = "TYPE_BOOL"
    UINT8 = "TYPE_UINT8"
    UINT16 = "TYPE_UINT16"
    UINT32 = "TYPE_UINT32"
    UINT64 = "TYPE_UINT64"
    INT8 = "TYPE_INT8"
    INT16 = "TYPE_INT16"
    INT32 = "TYPE_INT32"
    INT64 = "TYPE_INT64"
    FP16 = "TYPE_FP16"
    FP32 = "TYPE_FP32"
    FP64 = "TYPE_FP64"
    STRING = "TYPE_STRING"
    BF16 = "TYPE_BF16"


class BaseSignature(BaseModel):
    DataType: DataTypeEnum
    Dims: list[int]
    Name: str


class InputSignature(BaseSignature):
    MonitoringElement: str


class OutputSignature(BaseSignature):
    pass
