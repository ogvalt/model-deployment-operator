from typing import Annotated
from pydantic import BaseModel, PlainValidator, WithJsonSchema


xKubernetesPreserveUnknownFields = Annotated[
    object, 
    PlainValidator(lambda x: x),
    WithJsonSchema({"x-kubernetes-preserve-unknown-fields": "true", "type": "object"})
]

# class JobSpec(BaseModel):
#     class Config:
#         json_schema_extra = {
#             "$ref": "https://raw.githubusercontent.com/instrumenta/kubernetes-json-schema/133f84871ccf6a7a7d422cc40e308ae1c044c2ab/v1.10.7-local/jobspec-batch-v1.json",
#         }

# class ModelDeploymentSpec(BaseModel):
#     modelSource: str
#     jobImage: str
#     configMap: str
#     modelConfig: str = ""
#     jobSpec: JobSpec
    
class ModelDeploymentSpec(BaseModel):
    modelSource: str
    jobImage: str
    configMap: str
    modelConfig: str = ""
    jobSpec: xKubernetesPreserveUnknownFields = {}
 

