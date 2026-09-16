from pathlib import Path
import shutil
import uuid

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import HTMLResponse
from PIL import Image

ROOT = Path(__file__).parent
UPLOADS = ROOT / "uploads"
OUTPUTS = ROOT / "outputs"
UPLOADS.mkdir(exist_ok=True)
OUTPUTS.mkdir(exist_ok=True)

app = FastAPI(title="ASHStudio3D")

HTML = """<!doctype html>
<html><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'>
<title>ASHStudio Character AI</title>
<style>
body{font-family:-apple-system,BlinkMacSystemFont,sans-serif;background:#101114;color:#f5f5f5;margin:0}.wrap{max-width:1000px;margin:auto;padding:48px 24px}h1{font-size:42px;margin-bottom:8px}.sub{color:#aaa;margin-bottom:34px}.grid{display:grid;grid-template-columns:1fr 1fr;gap:18px}.card{background:#191b20;border:1px solid #30333b;border-radius:18px;padding:22px}.card input{width:100%}.label{font-size:18px;font-weight:700;margin-bottom:12px}.hint{color:#999;font-size:13px;margin-top:10px}button{margin-top:24px;width:100%;padding:16px;border:0;border-radius:14px;font-size:17px;font-weight:700;cursor:pointer}.status{margin-top:18px;color:#bbb}@media(max-width:650px){.grid{grid-template-columns:1fr}h1{font-size:32px}}
</style></head><body><div class='wrap'><h1>ASHStudio Character AI</h1><div class='sub'>Four T-pose references → local 3D character generation</div>
<form id='form'><div class='grid'>
<div class='card'><div class='label'>Front</div><input required name='front' type='file' accept='image/*'><div class='hint'>Full body, straight front view</div></div>
<div class='card'><div class='label'>Back</div><input required name='back' type='file' accept='image/*'><div class='hint'>Full body, straight back view</div></div>
<div class='card'><div class='label'>Left</div><input required name='left' type='file' accept='image/*'><div class='hint'>Full body, exact left profile</div></div>
<div class='card'><div class='label'>Right</div><input required name='right' type='file' accept='image/*'><div class='hint'>Full body, exact right profile</div></div>
</div><button>Prepare Character Generation</button></form><div id='status' class='status'>V1 validates and prepares the four views. Local AI generation is the next milestone.</div></div>
<script>document.getElementById('form').onsubmit=async(e)=>{e.preventDefault();let s=document.getElementById('status');s.textContent='Validating images…';let r=await fetch('/prepare',{method:'POST',body:new FormData(e.target)});let j=await r.json();s.textContent=r.ok?'✓ Four views prepared. Job '+j.job_id:(j.detail||'Error');};</script></body></html>"""

@app.get("/", response_class=HTMLResponse)
def home():
    return HTML

async def save_image(file: UploadFile, destination: Path):
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(400, f"{file.filename} is not an image")
    with destination.open("wb") as out:
        shutil.copyfileobj(file.file, out)
    try:
        with Image.open(destination) as image:
            image.verify()
    except Exception:
        destination.unlink(missing_ok=True)
        raise HTTPException(400, f"Could not read {file.filename}")

@app.post("/prepare")
async def prepare(front: UploadFile = File(...), back: UploadFile = File(...), left: UploadFile = File(...), right: UploadFile = File(...)):
    job_id = uuid.uuid4().hex[:12]
    job_dir = UPLOADS / job_id
    job_dir.mkdir(parents=True)
    for name, upload in (("front",front),("back",back),("left",left),("right",right)):
        await save_image(upload, job_dir / f"{name}.png")
    return {"job_id": job_id, "status": "prepared", "views": ["front","back","left","right"]}

@app.get("/health")
def health():
    return {"status": "ok"}
