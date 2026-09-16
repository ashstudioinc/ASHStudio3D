#!/bin/bash
set -e
cd "$(dirname "$0")/.."

if ! command -v brew >/dev/null 2>&1; then
  echo "ERROR: Homebrew is required for the isolated AI environment."
  echo "Install Homebrew from https://brew.sh then run this again."
  exit 1
fi

if ! brew list python@3.11 >/dev/null 2>&1; then
  echo "Installing Python 3.11..."
  brew install python@3.11
fi

PYTHON="$(brew --prefix python@3.11)/bin/python3.11"

if [ ! -d ".venv-ai" ]; then
  echo "Creating isolated AI environment..."
  "$PYTHON" -m venv .venv-ai
fi

source .venv-ai/bin/activate
python -m pip install --upgrade pip setuptools wheel

if [ ! -d "vendor/Hunyuan3D-2.1-mlx/.git" ]; then
  mkdir -p vendor
  echo "Cloning Apple-Silicon Hunyuan3D MLX backend..."
  git clone --depth 1 https://github.com/dgrauet/Hunyuan3D-2.1-mlx.git vendor/Hunyuan3D-2.1-mlx
fi

pip install mlx mlx-arsenal safetensors Pillow trimesh scikit-image PyMCubes scipy huggingface_hub

echo
echo "AI environment is ready."
echo "Model weights are intentionally NOT downloaded yet."
echo "Next run: ./ai/test_shape.command /absolute/path/to/character.png"
