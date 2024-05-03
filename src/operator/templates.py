import pathlib

import yaml
from jinja2 import Environment, FileSystemLoader


CURRENT_DIRECTORY = pathlib.Path(__file__).parent.resolve()
TEMPLATES_DIRECTORY = CURRENT_DIRECTORY / "templates"

template_env = Environment(loader=FileSystemLoader(str(TEMPLATES_DIRECTORY)))


def yaml_str_to_dict(yaml_str: str) -> dict:
    
    return yaml.safe_load(yaml_str)

def dict_to_yaml_str(dict_obj: dict) -> str:

    return yaml.dump(dict_obj, sort_keys=False)


def job_manifest_system_provided(
        modelName: str,
        namespace: str,
        jobType: str,
        modelSource: str,
        modelDest: str, 
        configMapName: str,
        jobImage: str
    ) -> str:

    template = template_env.get_template("job-operator.yaml")

    render = template.render(
        modelName=modelName,
        namespace=namespace,
        jobType=jobType,
        modelSource=modelSource,
        modelDest=modelDest,
        configMapName=configMapName,
        jobImage=jobImage
    )

    return render


def job_manifest_user_provided(
        modelName: str,
        namespace: str,
        jobType: str,
        spec: dict
) -> str:
    template = template_env.get_template("job-user-provided.yaml")

    render_without_spec = template.render(
        modelName=modelName,
        namespace=namespace,
        jobType=jobType,
    )

    render_dict = yaml_str_to_dict(render_without_spec)
    render_dict["spec"] = spec
    render = dict_to_yaml_str(render_dict)

    return render