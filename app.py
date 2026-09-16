from pathlib import Path
import io
import uuid

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import HTMLResponse
from PIL import Image, ImageOps

ROOT = Path(__file__).parent
UPLOADS = ROOT / "uploads"
OUTPUTS = ROOT / "outputs"
UPLOADS.mkdir(exist_ok=True)
OUTPUTS.mkdir(exist_ok=True)

app = FastAPI(title="ASHStudio3D")

HTML = """<!doctype html>
<html><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'>
<title>ASHStudio Character Generator</title>
<style>
*{box-sizing:border-box}body{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;background:#0c0d10;color:#f5f5f5;margin:0}.wrap{max-width:1050px;margin:auto;padding:48px 24px}h1{font-size:42px;margin:0 0 8px}.sub{color:#9da3ae;margin-bottom:30px}.grid{display:grid;grid-template-columns:1fr 1fr;gap:16px}.card{background:#17191e;border:1px solid #2c3038;border-radius:18px;padding:20px}.label{font-size:17px;font-weight:700;margin-bottom:12px}.hint{color:#8f96a3;font-size:13px;margin-top:10px}.preview{height:190px;border:1px dashed #3b404a;border-radius:12px;margin-bottom:13px;display:flex;align-items:center;justify-content:center;overflow:hidden;color:#777;background:#111318}.preview img{width:100%;height:100%;object-fit:contain}.actions{margin-top:22px}.generate{width:100%;padding:16px;border:0;border-radius:14px;font-size:17px;font-weight:750;cursor:pointer;background:#f2f2f2;color:#111}.generate:disabled{opacity:.5;cursor:not-allowed}.status{margin-top:18px;padding:16px;border-radius:12px;background:#15171b;color:#b7bdc8;line-height:1.5}.ok{color:#80d69d}.error{color:#ff9a9a}@media(max-width:650px){.grid{grid-template-columns:1fr}h1{font-size:32px}}
</style></head><body><div class='wrap'>
<h1>ASHStudio Character Generator</h1>
<div class='sub'>Upload four consistent full-body T-pose views. Files stay on this machine.</div>
<form id='form'><div class='grid'>
<div class='card'><div class='label'>Front</div><div class='preview' id='p-front'>Front preview</div><input required name='front' type='file' accept='image/*'><div class='hint'>Straight front view</div></div>
<div class='card'><div class='label'>Back</div><div class='preview' id='p-back'>Back preview</div><input required name='back' type='file' accept='image/*'><div class='hint'>Straight back view</div></div>
<div class='card'><div class='label'>Left</div><div class='preview' id='p-left'>Left preview</div><input required name='left' type='file' accept='image/*'><div class='hint'>Exact left profile</div></div>
<div class='card'><div class='label'>Right</div><div class='preview' id='p-right'>Right preview</div><input required name='right' type='file' accept='image/*'><div class='hint'>Exact right profile</div></div>
</div><div class='actions'><button id='generate' class='generate'>Prepare Character</button></div></form>
<div id='status' class='status'>Ready. The current milestone validates and normalizes the four source views before AI inference.</div>
</div>
<script>
const form=document.getElementById('form'), statusBox=document.getElementById('status'), button=document.getElementById('generate');
for(const input of form.querySelectorAll("input[type=file]")){input.addEventListener('change',()=>{const file=input.files[0],box=document.getElementById('p-'+input.name);if(!file){box.textContent=input.name+' preview';return}const url=URL.createObjectURL(file);box.innerHTML='';const img=document.createElement('img');img.src=url;img.onload=()=>URL.revokeObjectURL(url);box.appendChild(img);});}
form.addEventListener('submit',async(e)=>{e.preventDefault();button.disabled=true;button.textContent='Preparing…';statusBox.className='status';statusBox.textContent='Validating and normalizing four reference images…';try{const r=await fetch('/prepare',{method:'POST',body:new FormData(form)});const j=await r.json();if(!r.ok)throw new Error(j.detail||'Preparation failed');statusBox.className='status ok';statusBox.textContent='✓ Character references prepared. Job '+j.job_id+'. Next pipeline stage: local 3D inference.';}catch(err){statusBox.className='status error';statusBox.textContent='Error: '+err.message;}finally{button.disabled=false;button.textContent='Prepare Character';}});
</script></body></html>"""

@app.get("/", response_class=HTMLResponse)
def home():
    return HTML

async def save_image(file: UploadFile, destination: Path):
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(400, f"{file.filename} is not an image")
    data = await file.read()
    if len(data) > 20 * 1024 * 1024:
        raise HTTPException(400, f"{file.filename} is larger than 20 MB")
    try:
        with Image.open(io.BytesIO(data)) as source:
            image = ImageOps.exif_transpose(source).convert("RGB")
            if image.width < 256 or image.height < 256:
                raise HTTPException(400, f"{file.filename} is too small; use at least 256x256")
            image.thumbnail((2048, 2048), Image.Resampling.LANCZOS)
            image.save(destination, "PNG", optimize=True)
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(400, f"Could not read {file.filename}")

@app.post("/prepare")
async def prepare(front: UploadFile = File(...), back: UploadFile = File(...), left: UploadFile = File(...), right: UploadFile = File(...)):
    job_id = uuid.uuid4().hex[:12]
    job_dir = UPLOADS / job_id
    job_dir.mkdir(parents=True)
    try:
        for name, upload in (("front", front), ("back", back), ("left", left), ("right", right)):
            await save_image(upload, job_dir / f"{name}.png")
    except Exception:
        for path in job_dir.glob("*"):
            path.unlink(missing_ok=True)
        job_dir.rmdir()
        raise
    return {"job_id": job_id, "status": "prepared", "views": ["front", "back", "left", "right"]}

@app.get("/health")
def health():
    return {"status": "ok"}
