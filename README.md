# NSFW Identifier

(This project is under work as of August 27, 2025)

This project classifies images as whether it contains NSFW elements or not and outputs result accordingly. As of August 27, 2025, the project is under work. However, this current version allows you to run the model and classify images.

A lightweight **NSFW/SFW image classifier** built with [FalconsAI NSFW Image Detection](https://huggingface.co/Falconsai/nsfw_image_detection), Hugging Face Transformers, and Streamlit.  
The app allows single-image and batch classification with confidence scores and CSV export.  
Runs entirely **locally** (no images leave your machine) and supports **Apple Silicon acceleration (MPS)**.

## Features

- **Single image classification**: Upload an image → get NSFW/SFW label + confidence.
- **Batch mode**: Upload multiple images → tabular results + downloadable CSV.
- **Threshold tuning**: Adjust decision boundary interactively.
- **Hardware aware**: Automatically uses GPU (MPS on Apple Silicon, CUDA if available).
- **Exportable results**: CSV with filename, decision, confidence, and raw scores.

---

## Installation

```bash
git clone https://github.com/<your-username>/nsfw_identifier.git
cd nsfw_identifier

python3 -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt
```

You can run the app:
```bash
streamlit run app.py
```

---

## Evaluation
A small evaluation set of SFW, borderline, and NSFW images was tested.
(⚠️ For privacy/safety, actual NSFW images are not included in this repo. Only aggregate results and anonymized outputs are shared.)

[Table will be insterted here]

| filename       | decision | confidence | nsfw\_score | device |
| -------------- | -------- | ---------- | ----------- | ------ |
| img\_sfw1.jpg  | SFW      | 0.993      | 0.0067      | mps    |
| img\_sfw2.jpg  | SFW      | 0.999      | 0.0001      | mps    |
| img\_nsfw1.jpg | NSFW     | 0.9998     | 0.9998      | mps    |
| img\_nsfw2.jpg | NSFW     | 0.9977     | 0.9977      | mps    |

## Next Steps
- Add larger evaluation set with more borderline examples.
- Collect stats at different thresholds (precision/recall tradeoff).
- Explore fine-tuning on a multi-class dataset (e.g., "artistic nudity" vs "pornographic").
- Package as a lightweight API or browser extension demo.

## Disclaimer
This project is intended only for educational and research purposes.
It is not production-ready and should not be used in environments where content safety is critical without further evaluation and fine-tuning.
