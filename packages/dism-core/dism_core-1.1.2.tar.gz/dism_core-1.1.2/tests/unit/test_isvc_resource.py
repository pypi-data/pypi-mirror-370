import pytest

from dism_core.properties.isvc.tritonserver.torchscript import TorchscriptProperties
from dism_core.resources.isvc import InferenceServiceResource
from dism_core.resources.isvc.types import ModelType, ServingFrameworkType
from dism_core.resources.types import ResourceType


@pytest.fixture
def valid_resource() -> dict:
    return {
        "Type": "InferenceService::Tritonserver::Torchscript",
        "Workspace": "jetmet",
        "Properties": {
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
        },
    }


def test_resource(valid_resource):
    resource = InferenceServiceResource(**valid_resource)
    assert resource.SuperType == ResourceType.INFERENCE_SERVICE
    assert resource.ServingFrameworkType == ServingFrameworkType.TRITONSERVER
    assert resource.ModelType == ModelType.TORCHSCRIPT
    assert resource.Type == "InferenceService::Tritonserver::Torchscript"
    assert resource.Workspace == "jetmet"
    assert isinstance(resource.Properties, TorchscriptProperties)


def test_invalid_resource():
    with pytest.raises(
        NotImplementedError, match="Resource of type InferenceService::MLServer::Torchscript is not supported."
    ):
        InferenceServiceResource(
            **{"Type": "InferenceService::MLServer::Torchscript", "Workspace": "jetmet", "Properties": {}}
        )
