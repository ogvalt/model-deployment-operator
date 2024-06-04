import kopf
import kubernetes

from tritonclient.http import InferenceServerClient
from helpers import get_list_triton_pod_ip
from renderer.render import render_job, JobType

CRD_NAME = "modeldeployments"


@kopf.on.create(CRD_NAME)
def load_model(spec, name, namespace, logger, **kwargs):
    print(f"And here we are! Creating: {spec}")

    job_template = render_job(name, namespace, JobType.load, spec)

    kopf.adopt(job_template)

    api = kubernetes.client.BatchV1Api()
    obj = api.create_namespaced_job(
        body=job_template,
        namespace=namespace
    )

    logger.info(f"Load Job created: {obj}")

    return {'message': 'loading'}


class ModelStatus:
    NOT_EXISTS = "Not Exists"
    NOT_LOADED = "Not Loaded"
    LOADED = "Loaded"


@kopf.timer(CRD_NAME, interval=5.0)
def model_status(name, namespace, logger, **kwargs):
    model_version = ""

    urls = get_list_triton_pod_ip(namespace)

    list_model_exists: list[bool] = []

    for url in urls:
        client = InferenceServerClient(url)
        list_model_exists.append(client.is_model_ready(model_name=name, model_version=model_version))

    if all(list_model_exists):
        return ModelStatus.LOADED
    else:
        return ModelStatus.NOT_LOADED


@kopf.on.delete(CRD_NAME)
def unload_model(spec, name, namespace, logger, **kwargs):
    print(f"And here we are! Deleting: {spec}")

    job_template = render_job(name, namespace, JobType.unload, spec)

    api = kubernetes.client.BatchV1Api()
    obj = api.create_namespaced_job(
        body=job_template,
        namespace=namespace
    )

    logger.info(f"Unload Job created: {obj}")

    return {'message': 'unloading'}
