# app.py
import io
from PIL import Image
import pandas as pd
import streamlit as st
from nsfw_model import predict, predict_many

st.set_page_config(page_title="NSFW Identifier", page_icon="🔍", layout="centered")
st.title("🔍 NSFW Identifier (FalconsAI)")

tabs = st.tabs(["Single image", "Batch"])

with tabs[0]:
    st.write(
        "Upload an image to classify it as **NSFW** or **SFW**. "
        "You’ll also see a confidence score and raw model outputs."
    )

    uploaded = st.file_uploader("Choose an image...", type=["png", "jpg", "jpeg", "webp"])
    threshold = st.slider("NSFW decision threshold", 0.0, 1.0, 0.5, 0.01)

    if uploaded is not None:
        image_bytes = uploaded.read()
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        st.image(image, caption="Uploaded image", use_container_width=True)

        if st.button("Classify image"):
            with st.spinner("Running inference..."):
                result = predict(image)

            label = result["label"]
            conf  = result["confidence"]
            raw   = result["raw"]
            device = result["device"]

            # Try to find explicit NSFW score to apply threshold
            nsfw_score = None
            for o in raw:
                if o["label"].strip().lower() in {"nsfw", "adult", "explicit", "porn", "unsafe"}:
                    nsfw_score = o["score"]; break
            if nsfw_score is not None:
                effective_label = "NSFW" if nsfw_score >= threshold else "SFW"
                effective_conf  = nsfw_score if effective_label == "NSFW" else (1.0 - nsfw_score)
            else:
                effective_label, effective_conf = label, conf

            st.subheader("Result")
            st.markdown(
                f"**Prediction:** `{effective_label}`  \n"
                f"**Confidence:** `{effective_conf:.3f}`  \n"
                f"**Device:** `{device}`"
            )

            with st.expander("Show raw model outputs"):
                for o in raw:
                    st.write({k: (float(v) if k == "score" else v) for k, v in o.items()})

with tabs[1]:
    st.write("Upload **multiple** images to classify them in one go and export a CSV report.")
    files = st.file_uploader(
        "Choose images...", type=["png", "jpg", "jpeg", "webp"], accept_multiple_files=True
    )
    threshold_b = st.slider("NSFW decision threshold (batch)", 0.0, 1.0, 0.5, 0.01, key="thresh_batch")

    if files and st.button("Classify batch"):
        # Load all images
        pil_images = []
        filenames = []
        for f in files:
            try:
                img = Image.open(io.BytesIO(f.read())).convert("RGB")
                pil_images.append(img)
                filenames.append(f.name)
            except Exception as e:
                st.warning(f"Skipping {f.name}: {e}")

        if not pil_images:
            st.error("No valid images to process.")
        else:
            with st.spinner(f"Running inference on {len(pil_images)} images..."):
                results = predict_many(pil_images, batch_size=8)

            # Build a clean table
            rows = []
            for name, res in zip(filenames, results):
                raw = res["raw"]
                # Pull NSFW score if present to apply threshold
                nsfw_score = None
                sfw_score = None
                for o in raw:
                    lab = o["label"].strip().lower()
                    if lab in {"nsfw", "adult", "explicit", "porn", "unsafe"}:
                        nsfw_score = max(nsfw_score or 0.0, float(o["score"]))
                    if lab in {"sfw", "safe", "clean"}:
                        sfw_score = max(sfw_score or 0.0, float(o["score"]))

                if nsfw_score is not None:
                    decision = "NSFW" if nsfw_score >= threshold_b else "SFW"
                    decision_conf = nsfw_score if decision == "NSFW" else (1.0 - nsfw_score)
                else:
                    decision = res["label"]
                    decision_conf = res["confidence"]

                rows.append({
                    "filename": name,
                    "decision": decision,
                    "confidence": round(float(decision_conf), 4),
                    "device": res["device"],
                    "nsfw_score": round(float(nsfw_score or -1), 4),
                    "sfw_score": round(float(sfw_score or -1), 4),
                })

            df = pd.DataFrame(rows)
            st.dataframe(df, use_container_width=True)

            csv_bytes = df.to_csv(index=False).encode("utf-8")
            st.download_button(
                "⬇️ Download results as CSV",
                data=csv_bytes,
                file_name="nsfw_batch_results.csv",
                mime="text/csv",
            )
