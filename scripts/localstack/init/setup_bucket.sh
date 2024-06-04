#!/usr/bin/env bash

awslocal s3api create-bucket --bucket ${SETUP_BUCKET_NAME}  # Create bucket if it doesn't exist
awslocal s3 cp /models/model.graphdef s3://${SETUP_BUCKET_NAME}/model_repository/  # Upload the file
awslocal s3 ls --recursive s3://${SETUP_BUCKET_NAME}