#!/bin/bash
set -o pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "${DIR}/.." && pwd)"
source "${ROOT}/common.sh"

STEP="[patch_package]"
echo "${STEP} INFO: Patching package.json..."

echo "Patching package.json..."
(
  cd app && python3 "${ROOT}/lib/patch_package_json.py"
)