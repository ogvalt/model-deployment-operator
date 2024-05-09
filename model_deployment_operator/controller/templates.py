from typing import Literal
import pathlib

import yaml
from jinja2 import Environment, FileSystemLoader
from ..crd.model import ModelDeploymentSpec

CURRENT_DIRECTORY = pathlib.Path(__file__).parent.resolve()
TEMPLATES_DIRECTORY = CURRENT_DIRECTORY / "templates"

template_env = Environment(loader=FileSystemLoader(str(TEMPLATES_DIRECTORY)))


def yaml_str_to_dict(yaml_str: str) -> dict:
    return yaml.safe_load(yaml_str)


def dict_to_yaml_str(dict_obj: dict) -> str:
    return yaml.dump(dict_obj, sort_keys=False)


def job_manifest_system_provided(
        model_name: str,
        namespace: str,
        job_type: Literal["load"] | Literal["unload"],
        config_map_name: str,
        job_image: str,
        triton_urls: str,
        s_3_auth_file: str | None,
        model_spec: str,
) -> str:
    template = template_env.get_template("job-operator.yaml.jinja")

    render = template.render(
        modelName=model_name,
        namespace=namespace,
        jobType=job_type,
        configMapName=config_map_name,
        jobImage=job_image,
        tritonUrls=triton_urls,
        s3AuthFile=s_3_auth_file,
        modelSpec=model_spec,
    )

    return render


def job_manifest_user_provided(
        model_name: str,
        namespace: str,
        job_type: str,
        spec: dict
) -> str:
    template = template_env.get_template("job-user-provided.yaml.jinja")

    render_without_spec = template.render(
        modelName=model_name,
        namespace=namespace,
        jobType=job_type,
    )

    render_dict = yaml_str_to_dict(render_without_spec)
    render_dict["spec"] = spec
    render = dict_to_yaml_str(render_dict)

    return render


def deal_with_spec(
    model_spec: dict,
) -> dict:
    spec_model = ModelDeploymentSpec(**model_spec)


