#!/bin/bash

set -o pipefail

STEP="[install_pack]"
echo "${STEP} INFO: Install Cloud Native Buildpacks (pack CLI)"

if [ ! -f /usr/local/bin/pack ]; then
  echo "${STEP} INFO: Downloading pack CLI..."
  curl -sSL "https://github.com/buildpacks/pack/releases/download/v0.39.0/pack-v0.39.0-linux.tgz" | tar -C /usr/local/bin/ --no-same-owner -xzv pack
else
  echo "${STEP} INFO: pack CLI found in cache, skipping download"
fi

pack version
