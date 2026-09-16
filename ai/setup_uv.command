#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")/.."

echo "ASHStudio3D isolated AI setup"
echo "This does not modify macOS system Python or Homebrew Python."

UV_DIR="$PWD/.tools/uv"
UV_BIN="$UV_DIR/uv"
mkdir -p "$UV_DIR"

if [ ! -x "$UV_BIN" ]; then
  echo "Downloading uv into the project only..."
  INSTALLER="$(mktemp)"
  curl -LsSf https://astral.sh/uv/install.sh -o "$INSTALLER"
  UV_INSTALL_DIR="$UV_DIR" sh "$INSTALLER"
  rm -f "$INSTALLER"
fi

echo "Installing an isolated Python 3.11 managed by uv..."
"$UV_BIN" python install 3.11

echo "Creating .venv-ai-uv..."
rm -rf .venv-ai-uv
"$UV_BIN" venv .venv-ai-uv --python 3.11

if [ ! -d "vendor/Hunyuan3D-2.1-mlx/.git" ]; then
  mkdir -p vendor
  echo "Cloning Hunyuan3D Apple-Silicon MLX backend..."
  git clone --depth 1 https://github.com/dgrauet/Hunyuan3D-2.1-mlx.git vendor/Hunyuan3D-2.1-mlx
fi

echo "Installing Stage-1 shape dependencies into .venv-ai-uv only..."
"$UV_BIN" pip install --python .venv-ai-uv/bin/python \
  mlx mlx-arsenal safetensors Pillow trimesh scikit-image PyMCubes scipy huggingface_hub

echo
echo "READY"
echo "No model weights have been downloaded yet."
echo "Next command: ./ai/test_uv_shape.command /absolute/path/to/reference.png"
