#!/bin/sh
set -e

kopf run /workdir/src/model-deployment-operator.py \
    -A \
    --log-format=json \
    --liveness http://0.0.0.0:8003/healthz