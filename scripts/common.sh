#!/bin/bash

if [ -f "/tmp/build.env" ]; then
  source "/tmp/build.env"
fi

notify_deploy_failed() {
  local reason="$1"
  echo "[notify_deploy_failed] INFO: Triggering failure notification. Reason: ${reason}"

  if [ -z "${AMPLIFY_DEPLOY_FAILED_URL:-}" ]; then
    echo "[notify_deploy_failed] AMPLIFY_DEPLOY_FAILED_URL not set, skipping webhook notify"
    return 0
  fi

  local safe_reason="${reason//\"/\'}"
  local ts
  ts="$(date +%s)"

  local payload
  payload=$(printf '{"userId":"%s","functionId":"%s","customRoutes":"%s","message":"%s","timestamp":%s}' \
    "${USER_ID:-}" "${FUNCTION_ID:-}" "${CUSTOM_ROUTES:-}" "${safe_reason}" "${ts}")

  echo "[notify_deploy_failed] INFO: Sending webhook to Amplify..."

  curl -sS -X POST \
    -H "Content-Type: application/json" \
    -d "${payload}" \
    "${AMPLIFY_DEPLOY_FAILED_URL}" \
    || echo "[notify_deploy_failed] WARN: failed to call Amplify webhook"
}

export -f notify_deploy_failed