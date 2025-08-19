from pydantic import BaseModel, Field, model_validator

from ...properties.isvc.mlserver import (
    LightGBMProperties,
    SKLearnProperties,
    XGBoostProperties,
)
from ...properties.isvc.tritonserver import (
    ONNXProperties,
    TensorflowSavedModelProperties,
    TorchscriptProperties,
)
from ..types import ResourceType
from .types import ModelType, ServingFrameworkType


class InferenceServiceResource(BaseModel):
    SuperType: ResourceType
    ServingFrameworkType: ServingFrameworkType
    ModelType: ModelType
    Type: str
    Workspace: str
    Properties: (
        TorchscriptProperties
        | TensorflowSavedModelProperties
        | ONNXProperties
        | XGBoostProperties
        | LightGBMProperties
        | SKLearnProperties
    ) = Field(...)

    @model_validator(mode="before")
    @classmethod
    def validate_and_map_props(cls, resource):
        try:
            super_type, framework, model = resource["Type"].split("::")
        except ValueError as err:
            raise ValueError(
                f"Invalid Type format: {resource['Type']}. Expected format: 'SuperType::Framework::Model'."
            ) from err

        # Validate the components
        if super_type != ResourceType.INFERENCE_SERVICE:
            raise NotImplementedError(f"Unsupported SuperType: {super_type}")
        if framework not in ServingFrameworkType.__members__.values():
            raise NotImplementedError(f"Unsupported ServingFramework: {framework}")
        if model not in ModelType.__members__.values():
            raise NotImplementedError(f"Unsupported ModelType: {model}")

        # Map the resource to the appropriate properties
        match (framework, model):
            case (ServingFrameworkType.TRITONSERVER, ModelType.TORCHSCRIPT):
                props = TorchscriptProperties(**resource["Properties"])
            case (ServingFrameworkType.TRITONSERVER, ModelType.TENSORFLOW_SAVEDMODEL):
                props = TensorflowSavedModelProperties(**resource["Properties"])
            case (ServingFrameworkType.TRITONSERVER, ModelType.ONNX):
                props = ONNXProperties(**resource["Properties"])
            case (ServingFrameworkType.ML_SERVER, ModelType.XGBOOST):
                props = XGBoostProperties(**resource["Properties"])
            case (ServingFrameworkType.ML_SERVER, ModelType.LIGHTGBM):
                props = LightGBMProperties(**resource["Properties"])
            case (ServingFrameworkType.ML_SERVER, ModelType.SKLEARN):
                props = SKLearnProperties(**resource["Properties"])
            case _:
                raise NotImplementedError(f"Resource of type {resource['Type']} is not supported.")

        # Update the resource with the mapped properties
        resource["SuperType"] = ResourceType(super_type)
        resource["ServingFrameworkType"] = ServingFrameworkType(framework)
        resource["ModelType"] = ModelType(model)
        resource["Properties"] = props
        return resource
