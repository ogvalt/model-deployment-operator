# syntax=docker/dockerfile:1.7-labs 
ARG BASE_IMAGE="python"
ARG IMAGE_TAG=3.10-alpine
FROM ${BASE_IMAGE}:${IMAGE_TAG} as export_requirements_stage

ARG POETRY_VERSION=1.8.1

RUN pip install "poetry==${POETRY_VERSION}"

WORKDIR /workdir

COPY pyproject.toml poetry.lock ./

RUN poetry export --without-hashes -o requirements.txt

ARG BASE_IMAGE="python"
ARG IMAGE_TAG=3.10-alpine
FROM ${BASE_IMAGE}:${IMAGE_TAG} as job_image

WORKDIR /workdir

COPY --from=export_requirements_stage /workdir/requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt
ADD ./model_deployment_operator /workdir/model_deployment_operator
ENTRYPOINT ["python", "/workdir/model_deployment_operator/jobs/s3_to_triton.py"]