# syntax=docker/dockerfile:1.7-labs 
ARG BASE_IMAGE="python"
ARG IMAGE_TAG=3.10-alpine
FROM ${BASE_IMAGE}:${IMAGE_TAG} as export_requirements_stage

ARG UV_VERSION=0.7.3

RUN pip install "uv==${UV_VERSION}"

WORKDIR /workdir

COPY pyproject.toml uv.lock ./

RUN uv export --no-hashes --no-dev --no-emit-project --output-file requirements.txt

ARG BASE_IMAGE="python"
ARG IMAGE_TAG=3.10-alpine
FROM ${BASE_IMAGE}:${IMAGE_TAG} as job_image

WORKDIR /workdir

COPY --from=export_requirements_stage /workdir/requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt
ADD ./model_deployment_operator /workdir/model_deployment_operator
ENTRYPOINT ["python", "/workdir/model_deployment_operator/jobs/s3_to_triton.py"]
