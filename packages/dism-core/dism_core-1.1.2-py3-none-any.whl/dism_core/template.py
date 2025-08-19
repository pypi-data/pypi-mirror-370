import json
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field, model_validator

from .resources.isvc import InferenceServiceResource
from .resources.types import ResourceType
from .versions import TemplateFormatVersion


class Template(BaseModel):
    TemplateFormatVersion: TemplateFormatVersion
    Description: str
    Resources: dict[str, InferenceServiceResource] = Field(...)

    @staticmethod
    def validate_version_1(values: dict[str, Any]) -> dict[str, Any]:
        resources = values.get("Resources", {})
        mapped_resources = {}
        for key, resource in resources.items():
            try:
                super_type, _, _ = resource["Type"].split("::")
            except ValueError as err:
                raise ValueError(
                    f"Invalid Type format: {resource['Type']}. Expected format: 'SuperType::Framework::Model'."
                ) from err

            # Validate the components
            if super_type != ResourceType.INFERENCE_SERVICE:
                raise ValueError(f"Unsupported SuperType: {super_type}")

            match super_type:
                case ResourceType.INFERENCE_SERVICE.value:
                    mapped_resources[key] = InferenceServiceResource(**resource)
                case _:
                    raise NotImplementedError(f"Resource of type {resource['Type']} is not supported.")

        values["Resources"] = mapped_resources
        return values

    @model_validator(mode="before")
    @classmethod
    def validate_and_map_resource(cls, values: dict[str, dict]) -> dict[str, InferenceServiceResource]:
        version = TemplateFormatVersion(values.get("TemplateFormatVersion"))
        match version:
            case TemplateFormatVersion.VERSION_1:
                return Template.validate_version_1(values)

    @classmethod
    def from_json_file(cls, file_path: str | Path) -> "Template":
        with open(file_path) as file:
            data = json.load(file)
        return cls(**data)

    @classmethod
    def from_json_str(cls, json_string: str) -> "Template":
        data = json.loads(json_string)
        return cls(**data)

    @classmethod
    def from_yaml_file(cls, file_path: str | Path) -> "Template":
        with open(file_path) as file:
            data = yaml.safe_load(file)
        return cls(**data)

    @classmethod
    def from_yaml_str(cls, yaml_string: str) -> "Template":
        data = yaml.safe_load(yaml_string)
        return cls(**data)

    def to_dict(self) -> dict[str, Any]:
        return self.model_dump(mode="json")

    def to_json(self, fpath: str | Path) -> None:
        with open(fpath, "w") as file:
            json.dump(self.to_dict(), file, indent=4)

    def to_yaml(self, fpath: str | Path) -> None:
        with open(fpath, "w") as file:
            yaml.safe_dump(self.to_dict(), file)
