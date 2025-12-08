#!/bin/bash

set -o pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "${DIR}/.." && pwd)"
source "${ROOT}/common.sh"

STEP="[publish_sqs]"
echo "${STEP} INFO: Post-build: send success message to SQS"

if [ -z "${ECR_REPO_NAME:-}" ] || [ -z "${IMAGE_REPO:-}" ] || [ -z "${IMAGE_TAG_FULL:-}" ]; then
  msg="Missing required ECR env: ECR_REPO_NAME / IMAGE_REPO / IMAGE_TAG_FULL"
  echo "${STEP} ERROR: ${msg}"
  notify_deploy_failed "${msg}"
  exit 1
fi

if [ -z "${SQS_URL:-}" ]; then
  msg="Missing SQS_URL env"
  echo "${STEP} ERROR: ${msg}"
  notify_deploy_failed "${msg}"
  exit 1
fi

echo "${STEP} INFO: Resolving image digest from ECR..."


IMAGE_DIGEST=$(aws ecr describe-images \
  --repository-name "${ECR_REPO_NAME}" \
  --image-ids imageTag="${IMAGE_TAG_FULL}" \
  --query 'imageDetails[0].imageDigest' \
  --output text)

if [ -z "${IMAGE_DIGEST}" ] || [ "${IMAGE_DIGEST}" = "None" ]; then
  msg="Failed to resolve image digest from ECR for tag ${IMAGE_TAG_FULL}"
  echo "${STEP} ERROR: ${msg}"
  notify_deploy_failed "${msg}"
  exit 1
fi

IMAGE_DIGEST_URI="${IMAGE_REPO}@${IMAGE_DIGEST}"
echo "${STEP} INFO: IMAGE_DIGEST=${IMAGE_DIGEST}"
echo "${STEP} INFO: IMAGE_DIGEST_URI=${IMAGE_DIGEST_URI}"

MESSAGE_BODY=$(printf '{"userId":"%s","functionId":"%s","ImageDigest":"%s","customRoutes":"%s"}' \
  "${USER_ID:-}" "${FUNCTION_ID:-}" "${IMAGE_DIGEST_URI}" "${CUSTOM_ROUTES:-}")


echo "${STEP} INFO: Sending message to SQS: ${MESSAGE_BODY}"

if ! aws sqs send-message \
  --queue-url "${SQS_URL}" \
  --message-body "${MESSAGE_BODY}" >/dev/null; then
  msg="Failed to send message to SQS"
  echo "${STEP} ERROR: ${msg}"
  notify_deploy_failed "${msg}"
  exit 1
fi

echo "${STEP} INFO: SQS message sent successfully."