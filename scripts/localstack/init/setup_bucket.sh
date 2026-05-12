#!/usr/bin/env bash

set -euo pipefail

awslocal s3api create-bucket --bucket "${SETUP_BUCKET_NAME}" || true
awslocal s3 cp /models/model.graphdef "s3://${SETUP_BUCKET_NAME}/model_repository/model.graphdef"
awslocal s3 ls --recursive "s3://${SETUP_BUCKET_NAME}"
