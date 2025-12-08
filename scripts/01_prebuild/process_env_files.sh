#!/bin/bash
set -o pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "${DIR}/.." && pwd)"
source "${ROOT}/common.sh"

STEP="[process_env]"
echo "${STEP} INFO: Processing custom environment variables..."

(
  cd app && python3 "${ROOT}/lib/create_env_file.py"
)
ENV_EXIT_CODE=$?

if [ ${ENV_EXIT_CODE} -ne 0 ]; then
  echo "${STEP} ERROR: Failed to create .env file"
  notify_deploy_failed "Failed to create .env file"
  exit 1
fi

if [ -f "./app/.env" ]; then
  echo "${STEP} INFO: .env file created successfully, generating wrapper..."
  (
    cd app && python3 "${ROOT}/lib/create_env_wrapper.py"
  )
  WRAPPER_EXIT_CODE=$?

  if [ ${WRAPPER_EXIT_CODE} -ne 0 ]; then
    echo "${STEP} ERROR: Failed to create env wrapper file"
    notify_deploy_failed "Failed to create env wrapper file"
    exit 1
  fi
fi