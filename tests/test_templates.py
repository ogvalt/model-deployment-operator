
import src.operator.templates as templates


def test_job_manifest_system_provided():
    
    model_name = "test_model"
    namespace = "triton"
    job_type = "load"
    model_source = "s3://my-bucket/model.engine"
    model_destination = "tritonserver"
    config_map_name = "aws-creds"
    job_image = "my-image"

    job_template = templates.job_manifest_system_provided(
        modelName=model_name,
        namespace=namespace,
        jobType=job_type,
        modelSource=model_source,
        modelDest=model_destination,
        configMapName=config_map_name,
        jobImage=job_image,
    )
    assert job_template


def test_job_manifest_user_provided():
    model_name = "test_model"
    namespace = "triton"
    job_type = "load"
    spec={
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
        modelName=model_name,
        namespace=namespace,
        jobType=job_type,
        spec=spec
    )

    assert job_template