#!/bin/bash

set -o pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "${DIR}/.." && pwd)"
source "${ROOT}/common.sh"

STEP="[build_image]"
echo "${STEP} INFO: Create container image with Cloud Native Buildpacks"
echo "${STEP} INFO: Building image: ${IMAGE}"

if ! pack build "${IMAGE}" \
  --builder gcr.io/buildpacks/builder:latest \
  --path ./app \
  --pull-policy if-not-present \
  --trust-builder; then
  echo "${STEP} ERROR: pack build failed"
  notify_deploy_failed "pack build failed"
  exit 1
fi

echo "${STEP} INFO: Pushing image to Amazon ECR..."
if ! docker push "${IMAGE}"; then
  echo "${STEP} ERROR: docker push failed"
  notify_deploy_failed "docker push failed"
  exit 1
fi