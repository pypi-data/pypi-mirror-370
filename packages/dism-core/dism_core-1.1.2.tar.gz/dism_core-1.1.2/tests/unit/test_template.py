import json
from unittest.mock import mock_open, patch

import pytest
import yaml
from pydantic import ValidationError

from dism_core import Template
from dism_core.resources.isvc.types import ModelType, ServingFrameworkType
from dism_core.resources.types import ResourceType
from dism_core.versions import TemplateFormatVersion


@pytest.fixture
def valid_yaml():
    return """
TemplateFormatVersion: "2025-03-31"
Description: Example template
Resources:
    MyResource:
        Type: InferenceService::Tritonserver::Torchscript
        Workspace: test
        Properties:
            Description: Example description
            Name: autoencoder
            MetricKey: output_1
            BuiltinThreshold: false
            AnomalyThreshold: 0.1
            InputSignature:
            -
                Name: input_0
                MonitoringElement: JetMET/MET/pfMETT1/Cleaned/METSig
                DataType: TYPE_FP32
                Dims:
                    - -1
                    - 51
            OutputSignature:
            -
                Name: output_0
                DataType: TYPE_FP32
                Dims:
                    - -1
                    - 51
            -
                Name: output_1
                DataType: TYPE_FP32
                Dims:
                    - -1
            MaxBatchSize: 0
            ModelUri: example/model.pt
    """


@pytest.fixture
def valid_json():
    return """
    {
        "TemplateFormatVersion": "2025-03-31",
        "Description": "Example template",
        "Resources": {
            "MyResource": {
                "Type": "InferenceService::Tritonserver::Torchscript",
                "Workspace": "jetmet",
                "Properties": {
                    "Description": "Example description",
                    "Name": "autoencoder",
                    "MetricKey": "output_1",
                    "BuiltinThreshold": false,
                    "AnomalyThreshold": 0.1,
                    "InputSignature": [
                        {
                            "Name": "input_0",
                            "MonitoringElement": "JetMET/MET/pfMETT1/Cleaned/METSig",
                            "DataType": "TYPE_FP32",
                            "Dims": [-1, 51]
                        }
                    ],
                    "OutputSignature": [
                        {
                            "Name": "output_0",
                            "DataType": "TYPE_FP32",
                            "Dims": [-1, 51]
                        },
                        {
                            "Name": "output_1",
                            "DataType": "TYPE_FP32",
                            "Dims": [-1]
                        }
                    ],
                    "MaxBatchSize": 0,
                    "ModelUri": "example/model.pt"
                }
            }
        }
    }
    """


def common_assert(template):
    assert template.TemplateFormatVersion == TemplateFormatVersion.VERSION_1
    assert template.Description == "Example template"
    assert "MyResource" in template.Resources
    assert template.Resources["MyResource"].SuperType == ResourceType.INFERENCE_SERVICE
    assert template.Resources["MyResource"].ServingFrameworkType == ServingFrameworkType.TRITONSERVER
    assert template.Resources["MyResource"].ModelType == ModelType.TORCHSCRIPT
    assert template.Resources["MyResource"].Type == "InferenceService::Tritonserver::Torchscript"


def test_from_yaml_str_valid(valid_yaml):
    template = Template.from_yaml_str(valid_yaml)
    common_assert(template)


def test_from_json_str_valid(valid_json):
    template = Template.from_json_str(valid_json)
    common_assert(template)


def test_invalid_yaml_format():
    invalid_yaml = """
    TemplateFormatVersion: "1.0"
    Description: "Example template"
    Resources:
      MyResource:
        Type: "InvalidType"
    """
    with pytest.raises(ValidationError, match="validation error for Template"):
        Template.from_yaml_str(invalid_yaml)


def test_invalid_json_format():
    invalid_json = """
    {
        "TemplateFormatVersion": "1.0",
        "Description": "Example template",
        "Resources": {
            "MyResource": {
                "Type": "InvalidType"
            }
        }
    }
    """
    with pytest.raises(ValidationError, match="validation error for Template"):
        Template.from_json_str(invalid_json)


@patch("builtins.open", new_callable=mock_open)
def test_from_yaml_file_valid(mock_file, valid_yaml):
    mock_file.return_value.__enter__.return_value = valid_yaml
    template = Template.from_yaml_file("template.yaml")
    common_assert(template)


@patch("builtins.open", new_callable=mock_open)
def test_from_json_file_valid(mock_file, valid_json):
    mock_file.return_value.read.return_value = valid_json
    template = Template.from_json_file("template.json")
    common_assert(template)


@patch("builtins.open", new_callable=mock_open)
def test_file_not_found(mock_file):
    mock_file.side_effect = FileNotFoundError
    with pytest.raises(FileNotFoundError):
        Template.from_yaml_file("nonexistent.yaml")
    with pytest.raises(FileNotFoundError):
        Template.from_json_file("nonexistent.json")


def test_dictify(valid_yaml):
    template = Template.from_yaml_str(valid_yaml)
    template_dict = template.to_dict()
    assert isinstance(template_dict, dict)
    assert template_dict["TemplateFormatVersion"] == TemplateFormatVersion.VERSION_1.value
    assert template_dict["Description"] == "Example template"
    assert isinstance(template_dict["Resources"], dict)
    assert "MyResource" in template_dict["Resources"]
    assert template_dict["Resources"]["MyResource"]["SuperType"] == ResourceType.INFERENCE_SERVICE.value
    assert template_dict["Resources"]["MyResource"]["ServingFrameworkType"] == ServingFrameworkType.TRITONSERVER.value
    assert template_dict["Resources"]["MyResource"]["ModelType"] == ModelType.TORCHSCRIPT.value
    assert template_dict["Resources"]["MyResource"]["Type"] == "InferenceService::Tritonserver::Torchscript"


@patch("builtins.open", new_callable=mock_open)
def test_to_json(mock_file, valid_yaml):
    template = Template.from_yaml_str(valid_yaml)
    template.to_json("output.json")
    mock_file.assert_called_once_with("output.json", "w")
    call_args_list = mock_file().write.call_args_list
    written_data = "".join(call.args[0] for call in call_args_list)
    assert json.loads(written_data) == template.to_dict()


@patch("builtins.open", new_callable=mock_open)
def test_to_yaml(mock_file, valid_yaml):
    template = Template.from_yaml_str(valid_yaml)
    template.to_yaml("output.yaml")
    mock_file.assert_called_once_with("output.yaml", "w")
    call_args_list = mock_file().write.call_args_list
    written_data = "".join(call.args[0] for call in call_args_list)
    assert yaml.safe_load(written_data) == template.to_dict()
