#!/bin/bash

set -o pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "${DIR}/.." && pwd)"
source "${ROOT}/common.sh"

STEP="[s3_sync]"

echo "${STEP} INFO: Syncing function source from S3..."
rm -rf app
mkdir -p app

if ! aws s3 sync "${S3_URL}" ./app; then
  echo "${STEP} ERROR: Failed to sync from S3: ${S3_URL}"
  notify_deploy_failed "S3 sync failed"
  exit 1
fi

echo "${STEP} INFO: Validating S3 function source..."

if [ ! -f "./app/index.js" ]; then
  echo "${STEP} ERROR: index.js not found in S3 source. Build aborted."
  echo "${STEP} DEBUG: Checked path: ${S3_URL}"
  ls -al ./app || true

  notify_deploy_failed "index.js not found in S3 source"
  exit 1
fi

if [ ! -f "./app/package.json" ]; then
  echo "${STEP} WARN: package.json not found in S3 source."
  echo "${STEP} WARN: A default package.json will be created by patch_package_json.py"
fi

echo "${STEP} INFO: Checking JavaScript Syntax Errors..."
if ! node -c ./app/index.js; then
  echo "${STEP} ERROR: JavaScript Syntax Error detected in index.js. Build aborted."
  notify_deploy_failed "JavaScript Syntax Error in index.js"
  exit 1
fi

echo "${STEP} INFO: JavaScript syntax check passed."
