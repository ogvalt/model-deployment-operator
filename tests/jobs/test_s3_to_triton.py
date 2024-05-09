import os
import pytest
import testcontainers.localstack as localstack

from mypy_boto3_s3 import S3Client
from model_deployment_operator.jobs.s3_to_triton import S3FileDownloader, ModelRepository
from model_deployment_operator.crd.model import ModelSpec, ModelConfigSpec, VersionSpec, FileSpec, ModelDeploymentSpec

import triton_testcontainer as tritoncontainer
import tritonclient.http as tritonhttpclient

import numpy as np


@pytest.fixture
def setup_localstack_with_s3(request):
    region_name = "us-east-1"

    container = localstack.LocalStackContainer(region_name=region_name)
    container = container.with_services("s3")
    container = container.start()

    def remove():
        container.stop()

    request.addfinalizer(remove)

    return container


@pytest.fixture
def setup_triton(request):
    # start triton
    triton = tritoncontainer.TritonContainer(with_gpus=False)

    triton.start()

    def remove_triton_container():
        triton.stop()

    request.addfinalizer(remove_triton_container)

    return triton

@pytest.fixture
def setup_localstack(request, global_shared_datadir):
    """
    This fixture setup localstack
    """
    region_name = "us-east-1"

    container = localstack.LocalStackContainer(region_name=region_name)
    container = container.with_services("s3")
    container = container.start()

    def remove():
        container.stop()

    request.addfinalizer(remove)

    model_name = "simple"
    version = 1
    file_to_upload = global_shared_datadir / "models_repository" / model_name / str(version) / "model.graphdef"

    bucket = "ogvalt-repository"
    key = "best.graphdef"

    s3_client: S3Client = container.get_client("s3")
    s3_client.create_bucket(Bucket=bucket)

    s3_client.upload_file(
        Filename=file_to_upload,
        Bucket=bucket,
        Key=key
    )

    model_spec = ModelDeploymentSpec(
        model=ModelSpec(
            modelConfig=ModelConfigSpec(
                max_batch_size=8,
                platform="tensorflow_graphdef",
                input=[
                    {
                        "name": "INPUT0",
                        "data_type": "TYPE_INT32",
                        "dims": [16]
                    },
                    {
                        "name": "INPUT1",
                        "data_type": "TYPE_INT32",
                        "dims": [16]
                    }
                ],
                output=[
                    {
                        "name": "OUTPUT0",
                        "data_type": "TYPE_INT32",
                        "dims": [16]
                    },
                    {
                        "name": "OUTPUT1",
                        "data_type": "TYPE_INT32",
                        "dims": [16]
                    }
                ]
            ),
            labels=["class_0", "class_1"],
            versions=[
                VersionSpec(
                    version=version,
                    files=[
                        FileSpec(
                            name="model.graphdef",
                            source=f"s3://{bucket}/{key}"
                        )
                    ]
                )
            ]
        )
    )

    endpoint_url = container.get_url()
    aws_access_key_id = "testcontainers-localstack"
    aws_secret_access_key = "testcontainers-localstack"

    return {
        "region_name": region_name,
        "endpoint_url": endpoint_url,
        "aws_access_key_id": aws_access_key_id,
        "aws_secret_access_key": aws_secret_access_key
    }, {
        "model_name": model_name,
        "model_spec": model_spec.model_dump_json()
    }


def test_load_and_unload(setup_localstack):
    creds, model = setup_localstack

    downloader = S3FileDownloader(**creds)

    with tritoncontainer.TritonContainer(with_gpus=False) as tritonserver:
        client = tritonserver.get_client()

        repository = ModelRepository(
            destination=[tritonserver.get_url("http")],
            s3_downloader=downloader
        )
        repository.load(**model)

        metadata = client.get_model_metadata(model_name=model["model_name"], model_version="1")

        assert metadata

        inputs = []
        outputs = []
        inputs.append(tritonhttpclient.InferInput("INPUT0", [8, 16], "INT32"))
        inputs.append(tritonhttpclient.InferInput("INPUT1", [8, 16], "INT32"))

        # Initialize the data
        inputs[0].set_data_from_numpy(np.ones([8, 16], dtype=np.int32))
        inputs[1].set_data_from_numpy(np.zeros([8, 16], dtype=np.int32))

        outputs.append(tritonhttpclient.InferRequestedOutput("OUTPUT0"))
        outputs.append(tritonhttpclient.InferRequestedOutput("OUTPUT1"))

        results = client.infer(
            model["model_name"],
            inputs,
            model_version="1",
            outputs=outputs,
        )

        output0_data = results.as_numpy("OUTPUT0")
        output1_data = results.as_numpy("OUTPUT1")

        assert client.is_model_ready(model["model_name"], model_version="1")
        np.testing.assert_array_equal(output0_data, np.ones([8, 16], dtype=np.int32))
        np.testing.assert_array_equal(output1_data, np.ones([8, 16], dtype=np.int32))

        repository.unload(model["model_name"])

        assert not client.is_model_ready(model["model_name"], model_version="1")
