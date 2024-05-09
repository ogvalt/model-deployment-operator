import os
from urllib.parse import urlparse
import boto3.session
import tritonclient.http as httpclient
import fire
import boto3
from mypy_boto3_s3.client import S3Client

import logging
import json

from model_deployment_operator.crd.model import ModelDeploymentSpec

logger = logging.getLogger("model-deployment-operator")


class S3FileDownloader:
    def __init__(
            self,
            region_name: str = "us-east-1",
            endpoint_url: str | None = None,
            aws_access_key_id: str | None = None,
            aws_secret_access_key: str | None = None,
            config: boto3.session.Config = boto3.session.Config(signature_version='s3v4'),
            verify: bool | None = False
    ) -> None:

        self.s3_client: S3Client = boto3.client(
            service_name='s3',
            region_name=region_name,
            endpoint_url=endpoint_url,
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            config=config,
            verify=verify,
        )

    @classmethod
    def from_env_vars(cls):
        """This function initializes S3FileDownloader from environment variables"""

        aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID")
        if aws_access_key_id is None:
            raise EnvironmentError("AWS_ACCESS_KEY_ID is not set")

        aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")
        if aws_secret_access_key is None:
            raise EnvironmentError("AWS_ACCESS_KEY_ID is not set")

        aws_region = os.getenv("AWS_REGION", "us-east-1")
        aws_endpoint_url = os.getenv("AWS_ENDPOINT_URL", None)

        client = S3FileDownloader(
            region_name=aws_region,
            endpoint_url=aws_endpoint_url,
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
        )

        return client

    @classmethod
    def from_config_file(cls, path_to_config: os.PathLike):
        """
            This function initializes S3FileDownloader from config file.
            Expected file format is JSON.
            {
                "AWS_ACCESS_KEY_ID": xxx,
                "AWS_SECRET_ACCESS_KEY": xxx,
                "AWS_REGION": xxx,
                "AWS_ENDPOINT_URL": xxx
            }

        """
        with open(path_to_config, 'r') as f:
            config_dict: dict = json.load(f)

        aws_access_key_id = config_dict["AWS_ACCESS_KEY_ID"]
        aws_secret_access_key = config_dict["AWS_SECRET_ACCESS_KEY"]
        aws_region = config_dict.get("AWS_REGION", "us-east-1")
        aws_endpoint_url = config_dict.get("AWS_ENDPOINT_URL", None)

        client = S3FileDownloader(
            region_name=aws_region,
            endpoint_url=aws_endpoint_url,
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
        )

        return client

    def load_file_from_s3(self, bucket: str, key: str, local_path: os.PathLike):
        self.s3_client.download_file(Bucket=bucket, Key=key, Filename=str(local_path))
        return local_path

    def load_file_from_s3_as_bytes(self, bucket: str, key: str):
        response = self.s3_client.get_object(Bucket=bucket, Key=key)
        return response["Body"].read()


class ModelRepository:
    def __init__(self, destination: list[str],
                 s3_auth_file: os.PathLike | None = None,
                 s3_downloader: S3FileDownloader | None = None):
        """
        This class is responsible for uploading models to Triton server.

        Args:
            destination: list of Triton server URLs
            s3_auth_file: path to file with S3 credentials (see S3FileDownloader.from_config_file)

        """
        self.endpoints = [
            httpclient.InferenceServerClient(url=item, verbose=False) for item in destination
        ]

        if s3_downloader is not None:
            self.s3_downloader = s3_downloader
            return

        if s3_auth_file is None:
            self.s3_downloader = S3FileDownloader.from_env_vars()
        else:
            self.s3_downloader = S3FileDownloader.from_config_file(s3_auth_file)

    def load(
            self,
            model_name: str,
            model_spec: str
    ):
        """This function uploads model to Triton server

        Args:
            model_name: model name
            model_spec: path to model specification JSON formated string
        """
        model_spec: ModelDeploymentSpec = ModelDeploymentSpec.model_validate_json(model_spec)

        model_config_json = model_spec.model.modelConfig.model_dump_json()

        labels = model_spec.model.labels

        versions = model_spec.model.versions

        files = {}

        if labels is not None:
            label_bytes = b"\n".join(line.encode("utf-8") for line in labels)
            files[f"file:labels.txt"] = label_bytes

        for version in versions:
            version_number = version.version

            for file in version.files:
                file_key = file.name
                file_source = file.source

                parsed_file_source = urlparse(file_source)

                bucket = parsed_file_source.hostname
                key = parsed_file_source.path.lstrip('/')

                bytes_model = self.s3_downloader.load_file_from_s3_as_bytes(bucket, key)
                files[f"file:{version_number}/{file_key}"] = bytes_model

        for triton_client in self.endpoints:
            triton_client.load_model(
                model_name=model_name,
                config=model_config_json,
                files=files
            )
            logger.info(f"Model {model_name} loaded to {triton_client._parsed_url}.")

    def unload(
            self,
            model_name: str,
    ):
        for triton_client in self.endpoints:
            triton_client.unload_model(
                model_name=model_name
            )
            logger.info(f"Model {model_name} unloaded {triton_client._parsed_url}.")


if __name__ == '__main__':
    fire.Fire(ModelRepository)
