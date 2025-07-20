#!/usr/bin/env bash
set -euo pipefail

# Usage: ./setup.sh [env_name]
ENV_NAME="${1:-.venv}"

python3 -m venv "${ENV_NAME}"

# for Linux / macOS
source "${ENV_NAME}/bin/activate"

pip install --upgrade pip



pip install -r requirements.txt

echo "source ${ENV_NAME}/bin/activate"
