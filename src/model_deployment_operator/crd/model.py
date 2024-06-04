from typing import Annotated
from kube_crd_generator import BaseModel
from pydantic import PlainValidator, WithJsonSchema, Field

from .generated.triton_model_config import ModelConfig

xKubernetesPreserveUnknownFields = Field(
    json_schema_extra={
        "x-kubernetes-preserve-unknown-fields": "true",
        "type": "object"
    }
)

xKubernetesPreserveUnknownFieldsAnnotation = Annotated[
    object,
    PlainValidator(lambda x: x),
    WithJsonSchema({"x-kubernetes-preserve-unknown-fields": "true", "type": "object"})
]


class FileSpec(BaseModel):
    name: str
    source: str


class VersionSpec(BaseModel):
    version: int
    files: list[FileSpec]


class ModelSpec(BaseModel):
    config: ModelConfig
    labels: list[str] = []
    versions: list[VersionSpec]


class AuthSpec(BaseModel):
    type: str = ""
    name: str = ""


class JobSpec(BaseModel):
    source: str = ""
    auth: AuthSpec


class JobTemplate(BaseModel):
    provider: str = "operator"
    spec: JobSpec  # = xKubernetesPreserveUnknownFields


class ModelDeploymentSpec(BaseModel):
    model: ModelSpec
    jobTemplate: JobTemplate
