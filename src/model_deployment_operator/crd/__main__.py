import sys

from kube_crd_generator.schemabase import KubeResourceBase
from .model import ModelDeploymentSpec


class ModelDeployment(KubeResourceBase):
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


def main():
    print(ModelDeployment.crd_schema())
    return 0


sys.exit(main())
