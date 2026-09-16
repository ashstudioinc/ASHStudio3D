# ASHStudio3D

Free, local-first four-view 3D character generation experiment for Apple Silicon.

## V1 goal

Upload four consistent full-body T-pose references (front, back, left, right), generate a textured character locally, preview it, and export an FBX without paid generation APIs.

## Current milestone

The repository currently contains the lightweight local application shell. It validates and stores four reference images. The actual open-source 3D inference backend is deliberately being integrated separately so we can test memory/compatibility on an 18 GB M3 Pro before coupling it to the UI.

## Run on macOS

```bash
git clone https://github.com/ashstudioinc/ASHStudio3D.git
cd ASHStudio3D
chmod +x start.command
./start.command
```

The app opens at `http://127.0.0.1:8000`.

## Reference-image rules

Use the same character, outfit and proportions in every image. Use a full-body T-pose, straight orthographic-like front/back/left/right views, consistent lighting, and preferably a simple background.

## Planned pipeline

`4 views -> preprocessing -> local multi-view 3D inference -> mesh/texture -> Blender cleanup -> FBX -> browser download`

Large model weights, uploads and generated outputs stay local and are ignored by Git.
