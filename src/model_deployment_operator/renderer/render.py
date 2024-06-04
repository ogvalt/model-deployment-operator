from ..crd.model import ModelDeploymentSpec

from enum import Enum


class JobType(Enum):
    load = "load"
    unload = "unload"


class JobProvider(Enum):
    operator = "operator"
    user = "user"


class JobTemplate:

    def __init__(
            self,
            name: str,
            namespace: str,
            provider: str,
            job_type: str,
            spec: dict
    ):
        self.name = name
        self.namespace = namespace
        self.provider = provider
        self.job_type = job_type
        self.spec = spec

    def render(self):
        """Return serialized Job as dict.
        """
        manifest = {
            'apiVersion': 'batch/v1',
            'kind': 'Job',
            'metadata': {
                'name': f'{self.name}.{self.job_type}',
                'namespace': self.namespace,
                'labels': {
                    'model-deployment-operator/templateProvider': self.provider,
                    'model-deployment-operator/jobType': self.job_type,
                    'model-deployment-operator/modelName': self.name,
                }
            },
            'spec': self.spec
        }
        return manifest


def render_spec(job_type: str, container_image: str, args: str):
    job_spec = {
        'template': {
            'backoffLimit': 0,
            'ttlSecondsAfterFinished': 36000,
            'spec': {
                'restartPolicy': 'Never',
                'containers': [
                    {
                        'name': f'model-deployment-job-{job_type}',
                        'image': container_image,
                        'args': args,
                    }
                ]
            }
        }
    }

    return job_spec


from .s3 import S3_JOB_IMAGE, render_args

job_image_registry = {
    "s3": S3_JOB_IMAGE
}


def render_job(model_name: str, namespace: str, job_type: JobType, spec: dict):
    md_spec: ModelDeploymentSpec = ModelDeploymentSpec.validate(spec)

    if md_spec.jobTemplate.provider == JobProvider.user.name:
        template_spec = md_spec.jobTemplate.spec.dict()

    else:
        container_image = job_image_registry[md_spec.jobTemplate.spec.source]
        args = render_args(model_name, namespace, job_type,
                           md_spec.jobTemplate.spec, md_spec.model)

        template_spec = render_spec(
            job_type.name, container_image=container_image, args=args,
        )

    manifest = JobTemplate(
        name=model_name,
        namespace=namespace,
        provider=md_spec.jobTemplate.provider,
        job_type=job_type.name,
        spec=template_spec)

    return manifest.render()
