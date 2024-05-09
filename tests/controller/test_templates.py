import model_deployment_operator.controller.templates as templates

import kubernetes_validate
import yaml


def test_job_manifest_system_provided():
    model_name = "test_model"
    namespace = "triton"
    job_type = "load"
    config_map_name = "aws-creds"
    job_image = "my-image"
    list_triton_url = "triton_test1, triton_test2"
    s3_auth_file = "/config/creds"
    model_spec = "{'a': 'b'}"

    job_template = templates.job_manifest_system_provided(
        model_name=model_name,
        namespace=namespace,
        job_type=job_type,
        config_map_name=config_map_name,
        job_image=job_image,
        triton_urls=list_triton_url,
        s_3_auth_file=s3_auth_file,
        model_spec=model_spec,
    )
    assert kubernetes_validate.validate(yaml.safe_load(job_template), desired_version="1.22")

    job_template = templates.job_manifest_system_provided(
        model_name=model_name,
        namespace=namespace,
        job_type="unload",
        config_map_name=config_map_name,
        job_image=job_image,
        triton_urls=list_triton_url,
        s_3_auth_file=s3_auth_file,
        model_spec=model_spec,
    )
    assert kubernetes_validate.validate(yaml.safe_load(job_template), desired_version="1.22")

    job_template = templates.job_manifest_system_provided(
        model_name=model_name,
        namespace=namespace,
        job_type="unload",
        config_map_name=config_map_name,
        job_image=job_image,
        triton_urls=list_triton_url,
        s_3_auth_file=None,
        model_spec=model_spec,
    )

    assert kubernetes_validate.validate(yaml.safe_load(job_template), desired_version="1.22")


def test_job_manifest_user_provided():
    model_name = "test_model"
    namespace = "triton"
    job_type = "load"
    spec = {
        "backoffLimit": 0,
        "ttlSecondsAfterFinished": 60,
        "template": {
            "spec": {
                "containers": [
                    {
                        "name": "test-model",
                        "image": "my-image",
                        "command": [
                            "python3",
                            "load_model.py"
                        ],
                        "env": [
                            {
                                "name": "MODEL_NAME",
                                "value": "test_model"
                            }
                        ]
                    }
                ]
            }
        }
    }

    job_template = templates.job_manifest_user_provided(
        model_name=model_name,
        namespace=namespace,
        job_type=job_type,
        spec=spec
    )

    assert kubernetes_validate.validate(yaml.safe_load(job_template), desired_version="1.22")
