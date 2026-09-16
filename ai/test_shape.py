from pathlib import Path
import argparse
import os
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
VENDOR = ROOT / "vendor" / "Hunyuan3D-2.1-mlx"
sys.path.insert(0, str(VENDOR))

parser = argparse.ArgumentParser(description="ASHStudio3D Apple Silicon shape-generation smoke test")
parser.add_argument("image", type=Path)
parser.add_argument("--steps", type=int, default=20)
parser.add_argument("--resolution", type=int, default=192)
args = parser.parse_args()

image = args.image.expanduser().resolve()
if not image.exists():
    raise SystemExit(f"Input image not found: {image}")

out_dir = ROOT / "outputs" / "ai-test"
out_dir.mkdir(parents=True, exist_ok=True)
out_file = out_dir / f"{image.stem}_shape.glb"

print("ASHStudio3D - MLX shape test")
print(f"Input: {image}")
print(f"Steps: {args.steps}, octree resolution: {args.resolution}")
print("First run will download the open-source MLX model weights from Hugging Face.")
print("This can take a while; keep the Mac connected to power.")

from hy3dshape.hy3dshape.pipeline_mlx import ShapePipeline

started = time.time()
pipe = ShapePipeline.from_pretrained("dgrauet/hunyuan3d-2.1-mlx")
mesh = pipe(
    str(image),
    num_inference_steps=args.steps,
    guidance_scale=7.5,
    octree_resolution=args.resolution,
)
mesh.export(str(out_file))

elapsed = (time.time() - started) / 60
print(f"SUCCESS: {out_file}")
print(f"Elapsed: {elapsed:.1f} minutes")
