import os, time, uuid, json
from fastapi import FastAPI, UploadFile, File, Form, BackgroundTasks
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image, ImageDraw

BASE_DIR = os.path.join(os.path.dirname(__file__), "storage", "jobs")
os.makedirs(BASE_DIR, exist_ok=True)

app = FastAPI(title="Group Selfie Backend (MVP Shell)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # lock later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def job_dir(job_id: str) -> str:
    d = os.path.join(BASE_DIR, job_id)
    os.makedirs(d, exist_ok=True)
    return d

def set_status(job_id: str, status: str, progress: float, message: str, result_url: str | None = None):
    path = os.path.join(job_dir(job_id), "status.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump({
            "job_id": job_id,
            "status": status,       # queued|running|done|failed
            "progress": progress,   # 0..1
            "message": message,
            "result_url": result_url
        }, f)

def read_status(job_id: str):
    path = os.path.join(job_dir(job_id), "status.json")
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_file(job_id: str, filename: str, data: bytes):
    path = os.path.join(job_dir(job_id), filename)
    with open(path, "wb") as f:
        f.write(data)

def run_mock_pipeline(job_id: str, env_prompt: str):
    try:
        set_status(job_id, "running", 0.1, "Saving inputs...")
        time.sleep(1)

        set_status(job_id, "running", 0.5, "Mock generating output...")
        time.sleep(2)

        # Create a placeholder output image (for now)
        img = Image.new("RGB", (1024, 768), color=(245, 245, 245))
        draw = ImageDraw.Draw(img)
        text = f"MOCK OUTPUT\n\nEnvironment prompt:\n{env_prompt}\n\nNext: plug real generator + verifier"
        draw.multiline_text((60, 60), text, fill=(20, 20, 20), spacing=8)

        out_path = os.path.join(job_dir(job_id), "final.jpg")
        img.save(out_path, "JPEG", quality=90)

        set_status(job_id, "done", 1.0, "Done!", result_url=f"/files/{job_id}/final.jpg")
    except Exception as e:
        set_status(job_id, "failed", 1.0, f"Failed: {e}")

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/generate")
async def generate(
    background_tasks: BackgroundTasks,
    env_prompt: str = Form(...),
    selfie_a: UploadFile = File(...),
    selfie_b: UploadFile = File(...),
):
    job_id = str(uuid.uuid4())
    set_status(job_id, "queued", 0.0, "Queued")

    a_bytes = await selfie_a.read()
    b_bytes = await selfie_b.read()
    save_file(job_id, "selfie_a.jpg", a_bytes)
    save_file(job_id, "selfie_b.jpg", b_bytes)

    background_tasks.add_task(run_mock_pipeline, job_id, env_prompt)
    return {"job_id": job_id}

@app.get("/status/{job_id}")
def status(job_id: str):
    s = read_status(job_id)
    if not s:
        return JSONResponse(status_code=404, content={"error": "job not found"})
    return s

@app.get("/files/{job_id}/{filename}")
def files(job_id: str, filename: str):
    path = os.path.join(job_dir(job_id), filename)
    if not os.path.exists(path):
        return JSONResponse(status_code=404, content={"error": "file not found"})
    return FileResponse(path)
