#!/usr/bin/env bash
# Idempotent project bootstrap for the Cloud Agent environment.
# Creates a virtual environment and installs the package with dev extras.
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

python3 -m venv .venv
# shellcheck disable=SC1091
source .venv/bin/activate

python -m pip install --upgrade pip
python -m pip install -e ".[dev]"

echo "TradeLaunchGrokBot environment ready. Activate with: source .venv/bin/activate"
