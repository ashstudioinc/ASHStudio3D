#!/bin/bash
set -e
cd "$(dirname "$0")/.."

if [ $# -lt 1 ]; then
  echo "Usage: ./ai/test_shape.command /absolute/path/to/character.png"
  exit 1
fi

if [ ! -d ".venv-ai" ]; then
  echo "AI environment not found. Run ./ai/setup_ai.command first."
  exit 1
fi

source .venv-ai/bin/activate
python ai/test_shape.py "$1" --steps 20 --resolution 192
