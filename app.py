# app.py
import io
from PIL import Image
import streamlit as st
from nsfw_model import predict

st.set_page_config(page_title="NSFW Identifier", page_icon="🔍", layout="centered")

st.title("NSFW Identifier")
st.write(
    "Upload an image to classify whether it is **NSFW** or **SFW**. "
    "You’ll also see a confidence score and raw model outputs."
)

with st.sidebar:
    st.header("About")
    st.markdown(
        "- Model: `Falconsai/nsfw_image_detection`\n"
        "- Local inference (no image leaves your machine)\n"
        "- Built with Streamlit + Hugging Face Transformers"
    )

uploaded = st.file_uploader("Choose an image...", type=["png", "jpg", "jpeg", "webp"])

if uploaded is not None:
    # Load and show the image
    image_bytes = uploaded.read()
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    st.image(image, caption="Uploaded image", use_container_width=True)

    # Optional: adjustable threshold for a user-facing decision boundary
    threshold = st.slider("NSFW decision threshold", 0.0, 1.0, 0.5, 0.01,
                          help="Above this score, we call the image NSFW.")

    if st.button("Classify Image"):
        with st.spinner("Analyzin, please wait..."):
            result = predict(image)

        # Decision (using the threshold slider)
        label = result["label"]
        conf  = result["confidence"]
        raw   = result["raw"]
        device = result["device"]

        # If user wants to override with threshold:
        # We'll compute an 'effective label' based on threshold if we can find a NSFW score.
        nsfw_score = None
        for o in raw:
            if o["label"].strip().lower() in {"nsfw", "adult", "explicit", "porn", "unsafe"}:
                nsfw_score = o["score"]
                break

        if nsfw_score is not None:
            effective_label = "NSFW" if nsfw_score >= threshold else "SFW"
            effective_conf = nsfw_score if effective_label == "NSFW" else (1.0 - nsfw_score)
        else:
            # Fall back to the model's top decision
            effective_label = label
            effective_conf = conf

        st.subheader("Result")
        st.markdown(
            f"**Prediction:** `{effective_label}`  \n"
            f"**Confidence:** `{effective_conf:.3f}`  \n"
            f"**Device:** `{device}`"
        )

        with st.expander("Show raw model outputs"):
            for o in raw:
                st.write({k: (float(v) if k == "score" else v) for k, v in o.items()})

