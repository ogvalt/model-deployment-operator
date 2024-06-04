from ..crd.model import JobSpec, ModelSpec
from ..helpers import get_list_triton_pod_ip, get_config_map_data
from .render import JobType

S3_JOB_IMAGE = "popovych-labs/model-deployment-operator/job/s3:latest"


def render_args(
    model_name: str,
    namespace: str,
    job_type: JobType,
    job_spec: JobSpec,
    model_spec: ModelSpec,

):
    if not (job_spec.auth.type == "configMap"):
        raise NotImplementedError("Unknown auth type for s3")

    config_map_name = job_spec.auth.name

    triton_urls = get_list_triton_pod_ip(namespace=namespace)
    creds_str = get_config_map_data(namespace=namespace, name=config_map_name)

    args = [
        "--destination", ",".join(triton_urls),
        "--aws_access_key_id", creds_str["aws_access_key_id"],
        "--aws_secret_access_key", creds_str["aws_secret_access_key"],
        "--aws_region_name", creds_str["aws_region_name"],
        "--aws_endpoint_url", creds_str["aws_endpoint_url"],
    ]
    if job_type == JobType.load:
        args.extend(
            [
                "load",
                "--model_name", model_name,
                "--model_spec", model_spec.model_dump_json(),
            ]
        )
    else:
        args.extend(
            [
                "unload",
                "--model_name", model_name,
            ]
        )

    return args
