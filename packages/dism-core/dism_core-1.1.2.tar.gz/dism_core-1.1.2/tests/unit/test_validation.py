from pathlib import Path
from unittest.mock import mock_open, patch

import pytest

from dism_core import InferenceServiceValidator, Template
from dism_core.validation.utils import has_handler_class


@pytest.fixture
def valid_yaml():
    return """
TemplateFormatVersion: "2025-03-31"
Description: Deploys multiple models to spot anomalies in the JME METSig distribution
Resources:
  MetSigPyTorchAutoEncoder:
    Type: InferenceService::Tritonserver::Torchscript
    Workspace: jetmet
    Properties:
      Description: Spot anomalies in the MetSig distribution
      Name: metsig-torchscript-autoencoder
      MetricKey: output_1
      BuiltinThreshold: false
      AnomalyThreshold: 0.1
      InputSignature:
        - Name: input_0
          MonitoringElement: JetMET/MET/pfMETT1/Cleaned/METSig
          DataType: TYPE_FP32
          Dims:
            - -1
            - 51
      OutputSignature:
        - Name: output_0
          DataType: TYPE_FP32
          Dims:
            - -1
            - 51
        - Name: output_1
          DataType: TYPE_FP32
          Dims:
            - -1
      MaxBatchSize: 0
      ModelUri: examples/mldeploy/torchscript/model.pt
  MetSigTensorflowAutoEncoder:
    Type: InferenceService::Tritonserver::TensorflowSavedModel
    Workspace: jetmet
    Properties:
      Description: Spot anomalies in the MetSig distribution
      Name: metsig-tensorflow-autoencoder
      MetricKey: output_1
      BuiltinThreshold: false
      AnomalyThreshold: 0.1
      InputSignature:
        - Name: input_0
          MonitoringElement: JetMET/MET/pfMETT1/Cleaned/METSig
          DataType: TYPE_FP32
          Dims:
            - -1
            - 51
      OutputSignature:
        - Name: output_0
          DataType: TYPE_FP32
          Dims:
            - -1
            - 51
        - Name: output_1
          DataType: TYPE_FP32
          Dims:
            - -1
      MaxBatchSize: 0
      SavedModelUri: examples/mldeploy/tensorflow/
  MetSigOnnxAutoEncoder:
    Type: InferenceService::Tritonserver::ONNX
    Workspace: jetmet
    Properties:
      Description: Spot anomalies in the MetSig distribution
      Name: metsig-onnx-autoencoder
      MetricKey: output_1
      BuiltinThreshold: false
      AnomalyThreshold: 0.1
      InputSignature:
        - Name: input_0
          MonitoringElement: JetMET/MET/pfMETT1/Cleaned/METSig
          DataType: TYPE_FP32
          Dims:
            - -1
            - 51
      OutputSignature:
        - Name: output_0
          DataType: TYPE_FP32
          Dims:
            - -1
            - 51
        - Name: output_1
          DataType: TYPE_FP32
          Dims:
            - -1
      MaxBatchSize: 0
      ModelUri: examples/mldeploy/onnx/model.onnx
  MetSigXGBoostRegressor:
    Type: InferenceService::MLServer::XGBoost
    Workspace: jetmet
    Properties:
      Description: Spot anomalies in the MetSig distribution
      Name: metsig-xgboost-autoencoder
      MetricKey: avg_mse
      BuiltinThreshold: false
      AnomalyThreshold: 0.1
      InputSignature:
        - Name: input_0
          MonitoringElement: JetMET/MET/pfMETT1/Cleaned/METSig
          DataType: TYPE_FP32
          Dims:
            - -1
            - 51
      OutputSignature:
        - Name: reconstruction
          DataType: TYPE_FP32
          Dims:
            - -1
            - 51
        - Name: avg_mse
          DataType: TYPE_FP32
          Dims:
            - -1
      CodeUri: examples/mldeploy/xgboost/
      Handler: app.Handler
      ModelUri: examples/mldeploy/xgboost/0001.ubj
  MetSigLightGBMRegressor:
    Type: InferenceService::MLServer::SKLearn
    Workspace: jetmet
    Properties:
      Description: Spot anomalies in the MetSig distribution
      Name: metsig-lightgbm-autoencoder
      MetricKey: avg_mse
      BuiltinThreshold: false
      AnomalyThreshold: 0.1
      InputSignature:
        - Name: input_0
          MonitoringElement: JetMET/MET/pfMETT1/Cleaned/METSig
          DataType: TYPE_FP32
          Dims:
            - -1
            - 51
      OutputSignature:
        - Name: reconstruction
          DataType: TYPE_FP32
          Dims:
            - -1
            - 51
        - Name: avg_mse
          DataType: TYPE_FP32
          Dims:
            - -1
      CodeUri: examples/mldeploy/sklearn-lightgbm/
      Handler: app.Handler
      ModelUri: examples/mldeploy/sklearn-lightgbm/model.joblib
  MetSigNMFRegressor:
    Type: InferenceService::MLServer::SKLearn
    Workspace: jetmet
    Properties:
      Description: Spot anomalies in the MetSig distribution
      Name: metsig-nmf-autoencoder
      MetricKey: avg_mse
      BuiltinThreshold: false
      AnomalyThreshold: 0.1
      InputSignature:
        - Name: input_0
          MonitoringElement: JetMET/MET/pfMETT1/Cleaned/METSig
          DataType: TYPE_FP32
          Dims:
            - -1
            - 51
      OutputSignature:
        - Name: reconstruction
          DataType: TYPE_FP32
          Dims:
            - -1
            - 51
        - Name: avg_mse
          DataType: TYPE_FP32
          Dims:
            - -1
      CodeUri: examples/mldeploy/sklearn-nmf/
      Handler: app.Handler
      ModelUri: examples/mldeploy/sklearn-nmf/model.joblib
    """


@pytest.fixture
def template(valid_yaml):
    return Template.from_yaml_str(valid_yaml)


@pytest.fixture
def app_script():
    return """
import numpy as np
import xgboost as xgb
from datatype import datatype_to_dtype, dtype_to_datatype
from mlserver import MLModel
from mlserver.types import InferenceRequest, InferenceResponse, RequestInput, RequestOutput, ResponseOutput
from mlserver.utils import get_model_uri
from sklearn.preprocessing import MinMaxScaler


class Handler(MLModel):
    async def load(self):
        model_uri = await get_model_uri(self._settings)
        self.model_name = self._settings.name
        self.model_version = self._settings.version
        self.model = xgb.Booster(model_file=model_uri)
"""


def test_valid_uris(template, app_script):
    validator = InferenceServiceValidator(template)
    with patch("builtins.open", mock_open(read_data=app_script)):
        with patch.object(Path, "is_file", return_value=True):
            with patch.object(Path, "is_dir", return_value=True):
                validator()


def test_file_not_found(template, app_script):
    validator = InferenceServiceValidator(template)
    with patch("builtins.open", mock_open(read_data=app_script)):
        with patch.object(Path, "is_file", return_value=False):
            with patch.object(Path, "is_dir", return_value=True):
                with pytest.raises(ValueError, match="File .* not found or is not a file."):
                    validator()


def test_dir_not_found(template, app_script):
    validator = InferenceServiceValidator(template)
    with patch("builtins.open", mock_open(read_data=app_script)):
        with patch.object(Path, "is_file", return_value=True):
            with patch.object(Path, "is_dir", return_value=False):
                with pytest.raises(ValueError, match="Directory .* not found or is not a directory."):
                    validator()


def test_has_handler_class_not_found():
    mock_file_content = """
import something

class NotMyHandler(BaseHandler):
    pass
    """
    with patch("builtins.open", mock_open(read_data=mock_file_content)):
        result = has_handler_class("fake/path/to/handler.py", "MyHandler")
        assert result is False


def test_has_handler_class_with_spacing_variations():
    mock_file_content = """
class    MyHandler   (BaseHandler):
    pass
    """
    with patch("builtins.open", mock_open(read_data=mock_file_content)):
        result = has_handler_class("fake/path.py", "MyHandler")
        assert result is True
