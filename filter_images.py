# filter_images.py
import argparse
from pathlib import Path
from PIL import Image
import shutil
from nsfw_model import predict

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input_dir", type=str, help="Folder with images to classify")
    parser.add_argument("--out", type=str, default="filtered_output",
                        help="Output folder for safe/review/nsfw subfolders")
    parser.add_argument("--threshold", type=float, default=0.5,
                        help="Decision threshold for NSFW")
    parser.add_argument("--margin", type=float, default=0.1,
                        help="Margin for 'review zone' (uncertain predictions)")
    args = parser.parse_args()

    input_dir = Path(args.input_dir)
    out_dir = Path(args.out)
    safe_dir = out_dir / "safe"
    nsfw_dir = out_dir / "nsfw"
    review_dir = out_dir / "review"

    for d in [safe_dir, nsfw_dir, review_dir]:
        d.mkdir(parents=True, exist_ok=True)

    exts = {".png", ".jpg", ".jpeg", ".webp"}
    images = [p for p in input_dir.rglob("*") if p.suffix.lower() in exts]

    if not images:
        print(f"[!] No images found in {input_dir}")
        return

    for img_path in images:
        try:
            img = Image.open(img_path).convert("RGB")
        except Exception as e:
            print(f"[skip] {img_path}: {e}")
            continue

        res = predict(img)
        nsfw_score = None
        for o in res["raw"]:
            if o["label"].strip().lower() in {"nsfw", "adult", "explicit", "porn", "unsafe"}:
                nsfw_score = float(o["score"])
                break

        if nsfw_score is None:
            # fallback to model decision
            label = res["label"].lower()
            if label == "nsfw":
                nsfw_score = 1.0
            else:
                nsfw_score = 0.0

        # Decide based on threshold + margin
        if nsfw_score >= args.threshold + args.margin:
            dest = nsfw_dir
        elif nsfw_score <= args.threshold - args.margin:
            dest = safe_dir
        else:
            dest = review_dir

        shutil.copy(img_path, dest / img_path.name)
        print(f"[{dest.name.upper()}] {img_path.name} (nsfw_score={nsfw_score:.3f})")

    print("\n✅ Done. Results saved in:", out_dir)

if __name__ == "__main__":
    main()

