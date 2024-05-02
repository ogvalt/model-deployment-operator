import kopf
from triton_client import InferenceServerClient
from kubernetes.client.models import V1Job, V1JobSpec


CRD_NAME = "modeldeployments"
TRITON_HTTP_PORT = 8000
TRITON_SERVICE_NAME = "tritonserver"

def get_triton_url(namespace, service_name=TRITON_SERVICE_NAME, port = TRITON_HTTP_PORT):
    return f"{service_name}.{namespace}.svc.cluster.local:{port}"

@kopf.on.create(CRD_NAME)
def create_fn(spec, name, namespace, logger, **kwargs):
    print(f"And here we are! Creating: {spec}")

    url = get_triton_url(namespace)

    logger.info(url)

    client = InferenceServerClient(url)

    try:
        logger.info(client.get_server_metadata())
        logger.info(client.get_model_repository_index())
    except Exception as e:
        logger.error(e)


    # return {'message': 'hello world'}  # will be the new status

class ModelStatus:
    NOT_EXISTS = "Not Exists"
    NOT_LOADED = "Not Loaded"
    LOADED = "Loaded"

@kopf.timer(CRD_NAME, interval=5.0)
def model_status(name, namespace, logger, **kwargs):

    model_version = ""

    url = get_triton_url(namespace)
    client = InferenceServerClient(url)
    
    list_available_models = client.get_model_repository_index()

    is_model_exists = any(map(lambda x: x["name"] == name, list_available_models))

    if not is_model_exists:
        return ModelStatus.NOT_EXISTS

    if client.is_model_ready(model_name=name, model_version=model_version):
        return ModelStatus.LOADED 
    else:
        return ModelStatus.NOT_LOADED

# @kopf.on.delete(CRD_NAME)