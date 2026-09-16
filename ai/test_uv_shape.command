#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")/.."

if [ $# -lt 1 ]; then
  echo "Usage: ./ai/test_uv_shape.command /absolute/path/to/reference.png"
  exit 1
fi

if [ ! -x ".venv-ai-uv/bin/python" ]; then
  echo "AI environment not found. Run ./ai/setup_uv.command first."
  exit 1
fi

.venv-ai-uv/bin/python ai/test_shape.py "$1" --steps 20 --resolution 192
