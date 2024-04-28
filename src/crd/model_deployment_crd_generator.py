import schemabase
from pydantic import BaseModel, Field



class configMapRefElement(BaseModel):
    name: str


class configMapRefObj(BaseModel):
    configMapRef: configMapRefElement


# @dataclass
class EnvironmentVariable(BaseModel):
    name: str
    value: str


# @dataclass
class VolumeMount(BaseModel):
    name: str
    mountPath: str


# @dataclass
class Container(BaseModel):
    name: str
    image: str
    env: list[EnvironmentVariable] = []
    envFrom: list[configMapRefObj] = []
    volumeMounts: list[VolumeMount] = []


# @dataclass
class Volumes(BaseModel):
    name: str
    configMap: configMapRefObj


# @dataclass
class Spec(BaseModel):
    containers: list[Container] = []
    volumes: list[Volumes] = []
    restartPolicy: str = "Never"


# @dataclass
class PodTemplate(BaseModel):
    spec: Spec


# @dataclass
class JobTemplate(BaseModel):
    backoffLimit: int
    ttlSecondsAfterFinished: int
    template: PodTemplate


# @dataclass
class ModelDeploymentSpec(BaseModel):
    modelSource: str
    jobTemplate: JobTemplate


class ModelDeployment(schemabase.KubeResourceBase):
    __group__ = '{{ .Values.crd.group }}'
    __version__ = 'v1alpha1'
    __short_names__ = ["modeldepls", "modeldepl", "mds", "md"]

    spec = ModelDeploymentSpec
    additionalPrinterColumns = [
        {
            "name": "Children",
            "type": "string",
            "priority": 0,
            "jsonPath": ".status.create_fn.children",
            "description": "The children pods created."
        },
        {
            "name": "Status",
            "type": "string",
            "priority": 0,
            "jsonPath": ".status.model_status",
            "description": "Model status."
        },
        {
            "name": "Model Source",
            "type": "string",
            "priority": 0,
            "jsonPath": ".spec.modelSource",
            "description": "Model source."
        }
    ]


print(ModelDeployment.crd_schema())