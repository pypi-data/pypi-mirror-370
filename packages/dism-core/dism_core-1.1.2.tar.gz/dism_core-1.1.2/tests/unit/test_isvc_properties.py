from pathlib import Path

import pytest

from dism_core.properties.isvc.mlserver import LightGBMProperties, SKLearnProperties, XGBoostProperties
from dism_core.properties.isvc.signature import DataTypeEnum
from dism_core.properties.isvc.tritonserver import (
    ONNXProperties,
    TensorflowSavedModelProperties,
    TorchscriptProperties,
)
from dism_core.properties.isvc.tritonserver.types import PlatformType


@pytest.fixture
def valid_torchcript_properties() -> dict:
    return {
        "Description": "Example description",
        "Name": "autoencoder",
        "MetricKey": "output_1",
        "BuiltinThreshold": False,
        "AnomalyThreshold": 0.1,
        "InputSignature": [
            {
                "Name": "input_0",
                "MonitoringElement": "JetMET/MET/pfMETT1/Cleaned/METSig",
                "DataType": "TYPE_FP32",
                "Dims": [-1, 51],
            }
        ],
        "OutputSignature": [
            {"Name": "output_0", "DataType": "TYPE_FP32", "Dims": [-1, 51]},
            {"Name": "output_1", "DataType": "TYPE_FP32", "Dims": [-1]},
        ],
        "MaxBatchSize": 0,
        "ModelUri": "example/model.pt",
    }


@pytest.fixture
def valid_tensorflow_savedmodel_properties() -> dict:
    return {
        "Description": "Example description",
        "Name": "autoencoder",
        "MetricKey": "output_1",
        "BuiltinThreshold": False,
        "AnomalyThreshold": 0.1,
        "InputSignature": [
            {
                "Name": "input_0",
                "MonitoringElement": "JetMET/MET/pfMETT1/Cleaned/METSig",
                "DataType": "TYPE_FP32",
                "Dims": [-1, 51],
            }
        ],
        "OutputSignature": [
            {"Name": "output_0", "DataType": "TYPE_FP32", "Dims": [-1, 51]},
            {"Name": "output_1", "DataType": "TYPE_FP32", "Dims": [-1]},
        ],
        "MaxBatchSize": 0,
        "SavedModelUri": "example/saved_model",
    }


@pytest.fixture
def valid_onnx_properties() -> dict:
    return {
        "Description": "Example description",
        "Name": "autoencoder",
        "MetricKey": "output_1",
        "BuiltinThreshold": False,
        "AnomalyThreshold": 0.1,
        "InputSignature": [
            {
                "Name": "input_0",
                "MonitoringElement": "JetMET/MET/pfMETT1/Cleaned/METSig",
                "DataType": "TYPE_FP32",
                "Dims": [-1, 51],
            }
        ],
        "OutputSignature": [
            {"Name": "output_0", "DataType": "TYPE_FP32", "Dims": [-1, 51]},
            {"Name": "output_1", "DataType": "TYPE_FP32", "Dims": [-1]},
        ],
        "MaxBatchSize": 0,
        "ModelUri": "example/model.onnx",
    }


@pytest.fixture
def valid_xgboost_properties() -> dict:
    return {
        "Description": "Example description",
        "Name": "autoencoder",
        "MetricKey": "output_1",
        "BuiltinThreshold": False,
        "AnomalyThreshold": 0.1,
        "InputSignature": [
            {
                "Name": "input_0",
                "MonitoringElement": "JetMET/MET/pfMETT1/Cleaned/METSig",
                "DataType": "TYPE_FP32",
                "Dims": [-1, 51],
            }
        ],
        "OutputSignature": [
            {"Name": "output_0", "DataType": "TYPE_FP32", "Dims": [-1, 51]},
            {"Name": "output_1", "DataType": "TYPE_FP32", "Dims": [-1]},
        ],
        "CodeUri": "example/xgboost",
        "ModelUri": "example/xgboost/0001.ubj",
        "Handler": "app.Handler",
    }


@pytest.fixture
def valid_lightgbm_properties() -> dict:
    return {
        "Description": "Example description",
        "Name": "autoencoder",
        "MetricKey": "output_1",
        "BuiltinThreshold": False,
        "AnomalyThreshold": 0.1,
        "InputSignature": [
            {
                "Name": "input_0",
                "MonitoringElement": "JetMET/MET/pfMETT1/Cleaned/METSig",
                "DataType": "TYPE_FP32",
                "Dims": [-1, 51],
            }
        ],
        "OutputSignature": [
            {"Name": "output_0", "DataType": "TYPE_FP32", "Dims": [-1, 51]},
            {"Name": "output_1", "DataType": "TYPE_FP32", "Dims": [-1]},
        ],
        "CodeUri": "example/lightgbm",
        "ModelUri": "example/lightgbm/0001.txt",
        "Handler": "app.Handler",
    }


@pytest.fixture
def valid_sklearn_properties() -> dict:
    return {
        "Description": "Example description",
        "Name": "autoencoder",
        "MetricKey": "output_1",
        "BuiltinThreshold": False,
        "AnomalyThreshold": 0.1,
        "InputSignature": [
            {
                "Name": "input_0",
                "MonitoringElement": "JetMET/MET/pfMETT1/Cleaned/METSig",
                "DataType": "TYPE_FP32",
                "Dims": [-1, 51],
            }
        ],
        "OutputSignature": [
            {"Name": "output_0", "DataType": "TYPE_FP32", "Dims": [-1, 51]},
            {"Name": "output_1", "DataType": "TYPE_FP32", "Dims": [-1]},
        ],
        "CodeUri": "example/sklearn",
        "ModelUri": "example/sklearn/model.joblib",
        "Handler": "app.Handler",
    }


@pytest.fixture
def valid_custom_image_properties() -> dict:
    return {
        "Description": "Example description",
        "Name": "autoencoder",
        "MetricKey": "output_1",
        "BuiltinThreshold": False,
        "AnomalyThreshold": 0.1,
        "InputSignature": [
            {
                "Name": "input_0",
                "MonitoringElement": "JetMET/MET/pfMETT1/Cleaned/METSig",
                "DataType": "TYPE_FP32",
                "Dims": [-1, 51],
            }
        ],
        "OutputSignature": [
            {"Name": "output_0", "DataType": "TYPE_FP32", "Dims": [-1, 51]},
            {"Name": "output_1", "DataType": "TYPE_FP32", "Dims": [-1]},
        ],
        "CodeUri": "example/sklearn",
        "ModelUri": "example/sklearn/model.joblib",
        "Handler": "app.Handler",
        "Image": "seldonio/mlserver:1.5.0",
    }


@pytest.fixture
def valid_custom_resources_properties() -> dict:
    return {
        "Description": "Example description",
        "Name": "autoencoder",
        "MetricKey": "output_1",
        "BuiltinThreshold": False,
        "AnomalyThreshold": 0.1,
        "InputSignature": [
            {
                "Name": "input_0",
                "MonitoringElement": "JetMET/MET/pfMETT1/Cleaned/METSig",
                "DataType": "TYPE_FP32",
                "Dims": [-1, 51],
            }
        ],
        "OutputSignature": [
            {"Name": "output_0", "DataType": "TYPE_FP32", "Dims": [-1, 51]},
            {"Name": "output_1", "DataType": "TYPE_FP32", "Dims": [-1]},
        ],
        "CodeUri": "example/sklearn",
        "ModelUri": "example/sklearn/model.joblib",
        "Handler": "app.Handler",
        "Resources": {
            "Requests": {"cpu": "500m", "memory": "1Gi", "nvidia.com/gpu": "1"},
            "Limits": {"cpu": "1", "memory": "2Gi", "nvidia.com/gpu": "1"},
        },
    }


def common_assert(properties):
    assert properties.Description == "Example description"
    assert properties.Name == "autoencoder"
    assert properties.MetricKey == "output_1"
    assert properties.BuiltinThreshold is False
    assert properties.AnomalyThreshold == 0.1
    assert len(properties.InputSignature) == 1
    assert len(properties.OutputSignature) == 2
    assert properties.InputSignature[0].Name == "input_0"
    assert properties.InputSignature[0].MonitoringElement == "JetMET/MET/pfMETT1/Cleaned/METSig"
    assert properties.InputSignature[0].DataType == DataTypeEnum.FP32
    assert properties.InputSignature[0].Dims == [-1, 51]
    assert properties.OutputSignature[0].Name == "output_0"
    assert properties.OutputSignature[0].DataType == DataTypeEnum.FP32
    assert properties.OutputSignature[0].Dims == [-1, 51]
    assert properties.OutputSignature[1].Name == "output_1"
    assert properties.OutputSignature[1].DataType == DataTypeEnum.FP32
    assert properties.OutputSignature[1].Dims == [-1]


def test_torchscript(valid_torchcript_properties):
    props = TorchscriptProperties(**valid_torchcript_properties)
    common_assert(props)
    assert props.MaxBatchSize == 0
    assert props.ModelUri == Path("example/model.pt")
    assert props.Platform == PlatformType.TORCHSCRIPT
    with pytest.raises(AttributeError, match="Platform is a constant and cannot be changed."):
        props.Platform = "invalid"


def test_tensorflow_savedmodel(valid_tensorflow_savedmodel_properties):
    props = TensorflowSavedModelProperties(**valid_tensorflow_savedmodel_properties)
    common_assert(props)
    assert props.MaxBatchSize == 0
    assert props.SavedModelUri == Path("example/saved_model")
    assert props.Platform == PlatformType.TENSORFLOW_SAVEDMODEL
    with pytest.raises(AttributeError, match="Platform is a constant and cannot be changed."):
        props.Platform = "invalid"
    props.MaxBatchSize = 10


def test_onnx(valid_onnx_properties):
    props = ONNXProperties(**valid_onnx_properties)
    common_assert(props)
    assert props.MaxBatchSize == 0
    assert props.ModelUri == Path("example/model.onnx")
    assert props.Platform == PlatformType.ONNX
    with pytest.raises(AttributeError, match="Platform is a constant and cannot be changed."):
        props.Platform = "invalid"


def test_xgboost(valid_xgboost_properties):
    props = XGBoostProperties(**valid_xgboost_properties)
    common_assert(props)
    assert props.ModelUri == Path("example/xgboost/0001.ubj")
    assert props.CodeUri == Path("example/xgboost")


def test_lightgbm(valid_lightgbm_properties):
    props = LightGBMProperties(**valid_lightgbm_properties)
    common_assert(props)
    assert props.ModelUri == Path("example/lightgbm/0001.txt")
    assert props.CodeUri == Path("example/lightgbm")


def test_sklearn(valid_sklearn_properties):
    props = SKLearnProperties(**valid_sklearn_properties)
    common_assert(props)
    assert props.ModelUri == Path("example/sklearn/model.joblib")
    assert props.CodeUri == Path("example/sklearn")


def test_custom_image(valid_custom_image_properties):
    props = SKLearnProperties(**valid_custom_image_properties)
    common_assert(props)
    assert props.ModelUri == Path("example/sklearn/model.joblib")
    assert props.CodeUri == Path("example/sklearn")
    assert props.Image == "seldonio/mlserver:1.5.0"


def test_custom_resources(valid_custom_resources_properties):
    props = SKLearnProperties(**valid_custom_resources_properties)
    common_assert(props)
    assert props.ModelUri == Path("example/sklearn/model.joblib")
    assert props.CodeUri == Path("example/sklearn")
    assert props.Resources is not None
    assert props.Resources.Requests.cpu == "500m"
    assert props.Resources.Requests.memory == "1Gi"
    assert props.Resources.Requests.gpu == "1"
    assert props.Resources.Limits.cpu == "1"
    assert props.Resources.Limits.memory == "2Gi"
    assert props.Resources.Limits.gpu == "1"
