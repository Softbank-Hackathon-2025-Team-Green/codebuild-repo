#!/bin/bash

set -o pipefail

STEP="[resolve_env]"
echo "${STEP} INFO: Resolve env, compute S3/ECR info, login to ECR"

AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
AWS_DEFAULT_REGION="${AWS_DEFAULT_REGION:-$(aws configure get region)}"

echo "${STEP} INFO: AWS_ACCOUNT_ID=${AWS_ACCOUNT_ID}"
echo "${STEP} INFO: AWS_DEFAULT_REGION=${AWS_DEFAULT_REGION}"
echo "${STEP} INFO: PROJECT_NAME=${PROJECT_NAME}"
echo "${STEP} INFO: USER_CODE_BUCKET=${USER_CODE_BUCKET}"
echo "${STEP} INFO: SQS_URL=${SQS_URL}"
echo "${STEP} INFO: ECR_REPO_NAME=${ECR_REPO_NAME}"
echo "${STEP} INFO: USER_ID=${USER_ID}"
echo "${STEP} INFO: FUNCTION_ID=${FUNCTION_ID}"
echo "${STEP} INFO: IMAGE_TAG=${IMAGE_TAG}"
echo "${STEP} INFO: CUSTOM_ROUTES=${CUSTOM_ROUTES}"
echo "${STEP} INFO: CUSTOM_ENV=${CUSTOM_ENV}"
echo "${STEP} INFO: AMPLIFY_DEPLOY_FAILED_URL=${AMPLIFY_DEPLOY_FAILED_URL}"

S3_URL="s3://${USER_CODE_BUCKET}/users/${USER_ID}/functions/${FUNCTION_ID}"
IMAGE_REPO="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_DEFAULT_REGION}.amazonaws.com/${ECR_REPO_NAME}"
IMAGE_TAG_FULL="${FUNCTION_ID}-${IMAGE_TAG}"
IMAGE="${IMAGE_REPO}:${IMAGE_TAG_FULL}"

echo "${STEP} INFO: S3_URL=${S3_URL}"
echo "${STEP} INFO: IMAGE_REPO=${IMAGE_REPO}"
echo "${STEP} INFO: IMAGE_TAG_FULL=${IMAGE_TAG_FULL}"
echo "${STEP} INFO: IMAGE=${IMAGE}"

cat <<EOF > /tmp/build.env
export AWS_ACCOUNT_ID="${AWS_ACCOUNT_ID}"
export AWS_DEFAULT_REGION="${AWS_DEFAULT_REGION}"
export S3_URL="${S3_URL}"
export IMAGE_REPO="${IMAGE_REPO}"
export IMAGE_TAG_FULL="${IMAGE_TAG_FULL}"
export IMAGE="${IMAGE}"
export ECR_REPO_NAME="${ECR_REPO_NAME}"
export SQS_URL="${SQS_URL}"
export USER_ID="${USER_ID}"
export FUNCTION_ID="${FUNCTION_ID}"
export CUSTOM_ROUTES="${CUSTOM_ROUTES}"
export AMPLIFY_DEPLOY_FAILED_URL="${AMPLIFY_DEPLOY_FAILED_URL}"
EOF

echo "${STEP} INFO: Logging in to Amazon ECR..."
aws ecr get-login-password --region "${AWS_DEFAULT_REGION}" \
  | docker login --username AWS --password-stdin "${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_DEFAULT_REGION}.amazonaws.com"