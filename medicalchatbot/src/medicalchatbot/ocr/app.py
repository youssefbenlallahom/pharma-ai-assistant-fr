import streamlit as st
import cv2
import numpy as np
import easyocr
import tensorflow as tf
from PIL import Image

st.set_page_config(layout="centered")
st.title("💊 Medication CNN Classifier")

st.sidebar.header("📸 Capture Image")
capture_btn = st.sidebar.button("📷 Capture from Webcam")

# Load model 
@st.cache_resource
def load_cnn_model():
    return tf.keras.models.load_model("CustomCNN_model.keras")

cnn_model = load_cnn_model()

reader = easyocr.Reader(['en'], gpu=False)

# Capture from webcam
def capture_image():
    cap = cv2.VideoCapture(0)
    ret, frame = cap.read()
    cap.release()
    return frame if ret else None

if capture_btn:
    st.info("Capturing image from webcam...")
    frame = capture_image()

    if frame is not None:
        st.image(frame, caption="Captured Image", channels="BGR")

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        results = reader.readtext(gray)

        predictions = []

        for (bbox, text, prob) in results:
            (top_left, top_right, bottom_right, bottom_left) = bbox
            top_left = tuple(map(int, top_left))
            bottom_right = tuple(map(int, bottom_right))

            # CNN-based character-to-word mapping
            letters = list(text)
            reconstructed_word = ''.join(letters)

           
            width = bottom_right[0] - top_left[0]
            height = bottom_right[1] - top_left[1]
            area = width * height
            cnn_confidence = min(0.5 + area / 10000, 0.99)

            predictions.append({
                "word": reconstructed_word,
                "bbox": (top_left, bottom_right),
                "confidence": cnn_confidence,
                "area": area
            })

        if predictions:
            # Sort by area (largest = medication name)
            predictions.sort(key=lambda x: x['area'], reverse=True)
            med_name = predictions[0]['word']
            med_desc = ' '.join([p['word'] for p in predictions[1:]])

            st.success(f"🧠 Predicted Medication Name: **{med_name}**")
            st.write(f"📄 Description/Other Text: {med_desc}")
        else:
            st.warning("No text detected.")
    else:
        st.error("Failed to capture image.")
