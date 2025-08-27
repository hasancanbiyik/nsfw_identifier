# nsfw_model.py

from typing import Any, Dict, List, Tuple
import torch
from transformers import pipeline
from PIL import Image
from typing import Iterable


# Detect best available device (Apple Silicon -> MPS, else CUDA, else CPU)
def _pick_device() -> Tuple[str, int]:
    if torch.backends.mps.is_available():
        return "mps", 0  # streamlit/transformers use "device=0" for non-CPU accel
    if torch.cuda.is_available():
        return "cuda", 0
    return "cpu", -1

_DEVICE_STR, _DEVICE_INDEX = _pick_device()

# Lazy-load the pipeline so Streamlit cold start is fast
_PIPE = None

def get_classifier():
    global _PIPE
    if _PIPE is None:
        # "image-classification" works for HF image classifiers with proper config
        _PIPE = pipeline(
            task="image-classification",
            model="Falconsai/nsfw_image_detection",
            device=_DEVICE_INDEX  # -1 = CPU, 0 = first accelerator
        )
    return _PIPE

# Map model output to a simple {label: "NSFW"|"SFW", score: float}
# and keep raw scores for transparency
def predict(image) -> Dict[str, Any]:
    clf = get_classifier()

    # top_k=2 usually returns both classes if the model is binary
    outputs: List[Dict[str, Any]] = clf(image, top_k=2)

    # The model's label names can vary (e.g., "NSFW"/"SFW", "nsfw"/"safe")
    # We'll be robust and infer the top class, then normalize to NSFW/SFW.
    # Sort by score desc just in case.
    outputs = sorted(outputs, key=lambda x: x["score"], reverse=True)
    top_label = outputs[0]["label"].strip().lower()

    # Heuristic mapping
    nsfw_keywords = {"nsfw", "adult", "explicit", "porn", "unsafe"}
    sfw_keywords  = {"sfw", "safe", "clean"}

    if top_label in nsfw_keywords:
        final_label = "NSFW"
        confidence = outputs[0]["score"]
    elif top_label in sfw_keywords:
        final_label = "SFW"
        confidence = outputs[0]["score"]
    else:
        # Fallback: if unknown label naming, compare any NSFW-ish vs SFW-ish scores
        nsfw_score = 0.0
        sfw_score = 0.0
        for o in outputs:
            l = o["label"].strip().lower()
            if l in nsfw_keywords:
                nsfw_score = max(nsfw_score, o["score"])
            if l in sfw_keywords:
                sfw_score = max(sfw_score, o["score"])
        if nsfw_score >= sfw_score:
            final_label, confidence = "NSFW", nsfw_score
        else:
            final_label, confidence = "SFW", sfw_score

    return {
        "label": final_label,
        "confidence": float(confidence),
        "raw": outputs,
        "device": _DEVICE_STR,
    }

def predict_many(images: Iterable[Image.Image], batch_size: int = 8):
    """
    Run inference over many PIL Images.
    Returns a list of dicts in the same shape as predict(...).
    """
    clf = get_classifier()

    # Hugging Face pipelines support batching when you pass a list.
    # We’ll accumulate results per image to keep shapes consistent.
    results = []
    batch = []
    # Keep a mapping of index -> image to preserve order
    for img in images:
        batch.append(img)

        if len(batch) == batch_size:
            outputs_batch = clf(batch, top_k=2)
            # outputs_batch is a list (one list-of-dicts per image)
            for outputs in outputs_batch:
                outputs = sorted(outputs, key=lambda x: x["score"], reverse=True)
                top_label = outputs[0]["label"].strip().lower()
                nsfw_keywords = {"nsfw", "adult", "explicit", "porn", "unsafe"}
                sfw_keywords  = {"sfw", "safe", "clean"}
                if top_label in nsfw_keywords:
                    final_label = "NSFW"; confidence = outputs[0]["score"]
                elif top_label in sfw_keywords:
                    final_label = "SFW"; confidence = outputs[0]["score"]
                else:
                    nsfw_score = 0.0; sfw_score = 0.0
                    for o in outputs:
                        l = o["label"].strip().lower()
                        if l in nsfw_keywords: nsfw_score = max(nsfw_score, o["score"])
                        if l in sfw_keywords:  sfw_score  = max(sfw_score, o["score"])
                    if nsfw_score >= sfw_score:
                        final_label, confidence = "NSFW", nsfw_score
                    else:
                        final_label, confidence = "SFW", sfw_score
                results.append({
                    "label": final_label,
                    "confidence": float(confidence),
                    "raw": outputs,
                    "device": _DEVICE_STR,
                })
            batch = []

    # Flush any remaining images
    if batch:
        outputs_batch = clf(batch, top_k=2)
        for outputs in outputs_batch:
            outputs = sorted(outputs, key=lambda x: x["score"], reverse=True)
            top_label = outputs[0]["label"].strip().lower()
            nsfw_keywords = {"nsfw", "adult", "explicit", "porn", "unsafe"}
            sfw_keywords  = {"sfw", "safe", "clean"}
            if top_label in nsfw_keywords:
                final_label = "NSFW"; confidence = outputs[0]["score"]
            elif top_label in sfw_keywords:
                final_label = "SFW"; confidence = outputs[0]["score"]
            else:
                nsfw_score = 0.0; sfw_score = 0.0
                for o in outputs:
                    l = o["label"].strip().lower()
                    if l in nsfw_keywords: nsfw_score = max(nsfw_score, o["score"])
                    if l in sfw_keywords:  sfw_score  = max(sfw_score, o["score"])
                if nsfw_score >= sfw_score:
                    final_label, confidence = "NSFW", nsfw_score
                else:
                    final_label, confidence = "SFW", sfw_score
            results.append({
                "label": final_label,
                "confidence": float(confidence),
                "raw": outputs,
                "device": _DEVICE_STR,
            })

    return results

