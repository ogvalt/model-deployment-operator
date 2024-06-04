import os
from urllib.parse import urlparse
import boto3.session
import tritonclient.http as httpclient
import fire
import boto3
from mypy_boto3_s3.client import S3Client

import logging

from src.model_deployment_operator.crd.model import ModelSpec

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

    def load_file_from_s3(self, bucket: str, key: str, local_path: os.PathLike):
        self.s3_client.download_file(Bucket=bucket, Key=key, Filename=str(local_path))
        return local_path

    def load_file_from_s3_as_bytes(self, bucket: str, key: str):
        response = self.s3_client.get_object(Bucket=bucket, Key=key)
        return response["Body"].read()


class S3ToTritonScript:
    def __init__(
            self,
            destination: str,
            aws_access_key_id: str,
            aws_secret_access_key: str,
            aws_region_name: str = "us-east-1",
            aws_endpoint_url: str | None = None,
    ):
        """
        This class is responsible for uploading models to Triton server.

        Args:
            destination: comma separated list of urls to Triton server instances
            aws_access_key_id: AWS access key ID
            aws_secret_access_key: AWS secret access key
            aws_region_name: AWS region name
            aws_endpoint_url: AWS endpoint URL            

        """
        self.endpoints = [
            httpclient.InferenceServerClient(url=item, verbose=False) for item in destination.split(",")
        ]

        self.s3_downloader = S3FileDownloader(
            region_name=aws_region_name,
            endpoint_url=aws_endpoint_url,
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
        )

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
        model_spec: ModelSpec = ModelSpec.model_validate_json(model_spec)

        model_config_json = model_spec.config.model_dump_json()

        labels = model_spec.labels

        versions = model_spec.versions

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
    fire.Fire(S3ToTritonScript)
