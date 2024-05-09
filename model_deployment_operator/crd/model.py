from typing import Annotated
from pydantic import BaseModel, PlainValidator, WithJsonSchema, Field

xKubernetesPreserveUnknownFields = Annotated[
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


class ModelConfigSpec(BaseModel):
    max_batch_size: int
    input: list
    output: list
    platform: str


class ModelSpec(BaseModel):
    modelConfig: ModelConfigSpec = Field(json_schema_extra={"x-kubernetes-preserve-unknown-fields": "true", "type": "object"})
    labels: list[str] = []
    versions: list[VersionSpec]


class ModelDeploymentSpec(BaseModel):
    model: ModelSpec
    jobTemplate: xKubernetesPreserveUnknownFields = {}
