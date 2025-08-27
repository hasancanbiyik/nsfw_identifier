# batch_classify.py
import argparse
from pathlib import Path
from PIL import Image
import pandas as pd
from nsfw_model import predict_many

def main():
    p = argparse.ArgumentParser()
    p.add_argument("input_dir", type=str, help="Folder with images")
    p.add_argument("--threshold", type=float, default=0.5, help="NSFW decision threshold")
    p.add_argument("--out", type=str, default="nsfw_batch_results.csv")
    p.add_argument("--batch_size", type=int, default=8)
    args = p.parse_args()

    image_paths = []
    for ext in ("*.png", "*.jpg", "*.jpeg", "*.webp"):
        image_paths.extend(Path(args.input_dir).rglob(ext))
    if not image_paths:
        print("No images found.")
        return

    pil_images = []
    valid_paths = []
    for pth in image_paths:
        try:
            pil_images.append(Image.open(pth).convert("RGB"))
            valid_paths.append(pth)
        except Exception as e:
            print(f"Skipping {pth}: {e}")

    results = predict_many(pil_images, batch_size=args.batch_size)

    rows = []
    for pth, res in zip(valid_paths, results):
        nsfw_score = None
        sfw_score = None
        for o in res["raw"]:
            lab = o["label"].strip().lower()
            if lab in {"nsfw", "adult", "explicit", "porn", "unsafe"}:
                nsfw_score = max(nsfw_score or 0.0, float(o["score"]))
            if lab in {"sfw", "safe", "clean"}:
                sfw_score = max(sfw_score or 0.0, float(o["score"]))

        if nsfw_score is not None:
            decision = "NSFW" if nsfw_score >= args.threshold else "SFW"
            decision_conf = nsfw_score if decision == "NSFW" else (1.0 - nsfw_score)
        else:
            decision = res["label"]
            decision_conf = res["confidence"]

        rows.append({
            "path": str(pth),
            "decision": decision,
            "confidence": round(float(decision_conf), 4),
            "device": res["device"],
            "nsfw_score": round(float(nsfw_score or -1), 4),
            "sfw_score": round(float(sfw_score or -1), 4),
        })

    df = pd.DataFrame(rows)
    df.to_csv(args.out, index=False)
    print(f"Wrote {args.out} with {len(df)} rows.")

if __name__ == "__main__":
    main()

