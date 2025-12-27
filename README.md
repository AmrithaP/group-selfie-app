# Group Selfie App (Hackathon MVP)

Upload 2 selfies + an environment prompt and generate a combined selfie (Stage 1).
Currently uses a **mock generator** (returns a placeholder image) while we wire real diffusion models.

## Requirements
- Python 3.10+
- Node.js 16+ (this repo uses Next.js 13)
- Git

## Run backend (FastAPI)
```bash
cd backend
# activate venv first (Windows)
# venv\Scripts\activate
pip install fastapi uvicorn python-multipart pillow numpy opencv-python python-dotenv requests
uvicorn main:app --reload --port 8000
