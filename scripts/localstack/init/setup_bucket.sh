#!/usr/bin/env bash

set -euo pipefail

if awslocal s3api head-bucket --bucket "${SETUP_BUCKET_NAME}" >/dev/null 2>&1; then
  echo "Bucket ${SETUP_BUCKET_NAME} already exists; continuing."
else
  awslocal s3api create-bucket --bucket "${SETUP_BUCKET_NAME}"
fi

awslocal s3 cp /models/model.graphdef "s3://${SETUP_BUCKET_NAME}/model_repository/model.graphdef"
awslocal s3 ls --recursive "s3://${SETUP_BUCKET_NAME}"
