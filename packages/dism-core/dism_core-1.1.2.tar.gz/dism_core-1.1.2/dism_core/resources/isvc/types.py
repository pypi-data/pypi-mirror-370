from enum import Enum


class ServingFrameworkType(str, Enum):
    TRITONSERVER = "Tritonserver"
    ML_SERVER = "MLServer"


class ModelType(str, Enum):
    TORCHSCRIPT = "Torchscript"
    TENSORFLOW_SAVEDMODEL = "TensorflowSavedModel"
    ONNX = "ONNX"
    XGBOOST = "XGBoost"
    LIGHTGBM = "LightGBM"
    SKLEARN = "SKLearn"
