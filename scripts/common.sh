#!/usr/bin/env bash

notify_deploy_failed() {
  local msg="$1"

  if [ -z "${AMPLIFY_DEPLOY_FAILED_URL:-}" ]; then
    echo "AMPLIFY_DEPLOY_FAILED_URL not set, skip deploy failed webhook. message=${msg}"
    return
  fi

  echo "Notifying Amplify /api/deploy/failed ..."

  curl -s -X POST "${AMPLIFY_DEPLOY_FAILED_URL}" \
    -H "Content-Type: application/json" \
    -d "{\"userId\":\"${USER_ID}\",\"functionId\":\"${FUNCTION_ID}\",\"customRoutes\":\"${CUSTOM_ROUTES}\",\"message\":\"${msg}\",\"timestamp\":$(date +%s)}" \
    || echo "WARN: failed to call Amplify deploy failed webhook"
}
