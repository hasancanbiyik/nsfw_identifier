# NSFW Identifier

This project classifies images as whether it contains NSFW elements or not and outputs result accordingly. As of August 27, 2025, the project is under work. However, this current version allows you to run the model and classify images.

`feat: add batch classification support (multi-file upload + CSV export)`

## Description
This PR introduces batch image classification to the NSFW Identifier app.
- New feature: Users can upload multiple images at once.
- UI: Added a dedicated Batch tab in the Streamlit app.
- Output: Classification results are shown in a table with confidence scores and can be exported as a CSV file.
- Backend: Implemented predict_many() in nsfw_model.py for efficient batched inference.

## Notes
- Keeps single-image classification unchanged.
- CSV export improves usability for larger test sets.
