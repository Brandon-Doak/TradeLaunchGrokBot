#!/usr/bin/env bash
# Idempotent project bootstrap for the Cloud Agent environment.
# Creates a virtual environment and installs the package with dev extras.
#
# This script is defensive about its base image: some images ship Python
# without the stdlib venv/ensurepip package. When the committed
# `.cursor/Dockerfile` base is used, python3-venv is already present and the
# check below is a no-op; when the environment boots from a different base
# (e.g. a just-in-time default image), we install it here so setup still works.
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

if ! python3 -c 'import ensurepip' >/dev/null 2>&1; then
  echo "python venv module unavailable; installing python3-venv..."
  if command -v sudo >/dev/null 2>&1 && command -v apt-get >/dev/null 2>&1; then
    sudo apt-get update -qq
    sudo apt-get install -y -qq python3-venv
  elif command -v apt-get >/dev/null 2>&1; then
    apt-get update -qq
    apt-get install -y -qq python3-venv
  else
    echo "ERROR: cannot install python3-venv automatically on this image." >&2
    exit 1
  fi
fi

python3 -m venv .venv
# shellcheck disable=SC1091
source .venv/bin/activate

python -m pip install --upgrade pip
python -m pip install -e ".[dev]"

echo "TradeLaunchGrokBot environment ready. Activate with: source .venv/bin/activate"
