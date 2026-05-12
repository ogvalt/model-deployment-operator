#!/usr/bin/env bash

set -euo pipefail

CREATE_BUCKET_ERR_FILE="/tmp/localstack-create-bucket.err"
if ! awslocal s3api create-bucket --bucket "${SETUP_BUCKET_NAME}" 2>"${CREATE_BUCKET_ERR_FILE}"; then
  if grep -Eq "BucketAlreadyOwnedByYou|BucketAlreadyExists" "${CREATE_BUCKET_ERR_FILE}"; then
    echo "Bucket ${SETUP_BUCKET_NAME} already exists; continuing."
  else
    cat "${CREATE_BUCKET_ERR_FILE}" >&2
    exit 1
  fi
fi

awslocal s3 cp /models/model.graphdef "s3://${SETUP_BUCKET_NAME}/model_repository/model.graphdef"
awslocal s3 ls --recursive "s3://${SETUP_BUCKET_NAME}"
