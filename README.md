# 🔍 NSFW Identifier

A lightweight **NSFW/SFW image classifier** built with [FalconsAI NSFW Image Detection](https://huggingface.co/Falconsai/nsfw_image_detection), Hugging Face Transformers, and Streamlit.  
Extended with a **confidence-based filter pipeline** and a **Chrome extension prototype** for real-world integration.  
Runs entirely **locally** (no images leave your machine) and supports **Apple Silicon acceleration (MPS)**.

---

## Features

- **Single image classification (Streamlit)**  
  Upload an image → NSFW/SFW label + confidence.

- **Batch mode (Streamlit)**  
  Upload multiple images → table of results + downloadable CSV.

- **Confidence-based filtering (CLI)**  
  Sorts images into `safe/`, `review/`, and `nsfw/` subfolders using threshold + margin.

- **Chrome extension prototype (local demo)**  
  Right-click any image → classify via local API.  
  NSFW → blurred + red badge. SFW → green badge/outline.

---

## Installation

```bash
git clone https://github.com/hasancanbiyik/nsfw_identifier
cd nsfw_identifier

python3 -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt
```

---

## ▶Usage

### 1. Streamlit app
```bash
streamlit run app.py
```
- Single & batch classification via browser UI.

### 2. Confidence filter (CLI)
```bash
python filter_images.py <input_dir> --out results --threshold 0.5 --margin 0.1
```
- Outputs images into `safe/`, `review/`, and `nsfw/`.

### 3. FastAPI backend
```bash
uvicorn server:app --host 127.0.0.1 --port 8000 --reload
```
- Endpoints:  
  - `/health` → API status  
  - `/classify?url=...` → classify an image by URL  

### 4. Chrome extension
1. Start the FastAPI server.  
2. Go to `chrome://extensions` → enable **Developer mode**.  
3. **Load unpacked** → select the `extension/` folder.  
4. Right-click an image → **Check image with NSFW Identifier**.  
   - NSFW images blur + red badge with score.  
   - SFW images show green outline/badge.

---

## Evaluation

A small evaluation set of **SFW, borderline, and NSFW** images was tested.  
(⚠️ No NSFW images are included in this repo; only anonymized outputs are shown.)

| Type        | Samples | Correct | Accuracy |
|-------------|---------|---------|----------|
| SFW         | 10      | 10      | 100%     |
| NSFW        | 5       | 5       | 100%     |
| Borderline  | 5       | 4       | 80%      |

Example output (CSV excerpt):

| filename      | decision | confidence | nsfw_score | device |
|---------------|----------|-------------|------------|--------|
| img_sfw1.jpg  | SFW      | 0.993       | 0.0067     | mps    |
| img_nsfw1.jpg | NSFW     | 0.9998      | 0.9998     | mps    |

---

## Project Structure

```
nsfw_identifier/
├─ app.py              # Streamlit frontend
├─ nsfw_model.py       # Model loading + inference
├─ batch_classify.py   # Batch classification tool
├─ filter_images.py    # Confidence-based filtering
├─ server.py           # FastAPI backend for extension
├─ extension/          # Chrome extension (MV3)
├─ quick_eval.py       # Evaluation helper
├─ requirements.txt
└─ README.md
```

---

## 🛠Next Steps

- Expand evaluation dataset, especially borderline cases.  
- Add precision/recall metrics at multiple thresholds.  
- Package API + extension into a standalone demo.  
- Explore fine-tuning on a multi-class dataset (art vs explicit).  

---

## Disclaimer

This project is intended **only for educational and research purposes**.  
It is not production-ready and should not be used for production content moderation without further testing and refinement.  
All evaluations were performed locally; no images are uploaded to external services.
