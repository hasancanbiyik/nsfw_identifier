# server.py
import io
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from PIL import Image
import httpx
from nsfw_model import predict

app = FastAPI(title="NSFW Identifier API")

# Dev CORS: allow everything so the extension can call localhost
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # OK for local demo only
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ClassifyRequest(BaseModel):
    url: str

def _fetch_image(url: str) -> Image.Image:
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        r = httpx.get(url, headers=headers, timeout=10.0, follow_redirects=True)
        r.raise_for_status()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Fetch failed: {e}")
    try:
        return Image.open(io.BytesIO(r.content)).convert("RGB")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Decode failed: {e}")

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/classify")
def classify(body: ClassifyRequest):
    img = _fetch_image(body.url)
    result = predict(img)
    nsfw_score = None
    for o in result["raw"]:
        if o["label"].strip().lower() in {"nsfw","adult","explicit","porn","unsafe"}:
            nsfw_score = float(o["score"]); break
    return {
        "label": result["label"],
        "confidence": float(result["confidence"]),
        "nsfw_score": nsfw_score,
        "device": result["device"],
        "raw": result["raw"],
    }

# Handy GET variant: /classify?url=...
@app.get("/classify")
def classify_get(url: str = Query(...)):
    return classify(ClassifyRequest(url=url))

