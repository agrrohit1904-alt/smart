import streamlit as st
import cv2
from ultralytics import YOLO
import numpy as np

# Load the model once and cache it for speed
@st.cache_resource
def load_yolo():
    return YOLO('yolov8n.pt')

model = load_yolo()

st.title("🛡️ Smart Safety & Age Verification")

# Session state to track progress
if 'status' not in st.session_state:
    st.session_state.status = "START"

# --- STEP 1: PASSWORD ---
if st.session_state.status == "START":
    password = st.text_input("Enter Rider Password", type="password")
    if st.button("Submit Password"):
        if password == "1234":
            st.session_state.status = "AGE_CHECK"
            st.rerun()
        else:
            st.error("Incorrect Password")

# --- STEP 2: AGE CHECK ---
elif st.session_state.status == "AGE_CHECK":
    age = st.number_input("Enter your age", min_value=0, max_value=120)
    if st.button("Verify Age"):
        if age >= 18:
            st.session_state.status = "HELMET_SCAN"
            st.rerun()
        else:
            st.warning("Access Denied: You must be 18+ to operate this vehicle.")

# --- STEP 3: HELMET SCAN ---
elif st.session_state.status == "HELMET_SCAN":
    st.info("Please face the camera and ensure your helmet is visible.")
    img_file = st.camera_input("Take a photo for safety check")

    if img_file:
        # Convert to OpenCV format
        file_bytes = np.asarray(bytearray(img_file.read()), dtype=np.uint8)
        frame = cv2.imdecode(file_bytes, 1)
        
        # Run YOLO detection
        results = model(frame)
        
        # Check for helmet or headwear labels
        found_helmet = False
        for r in results:
            for box in r.boxes:
                label = model.names[int(box.cls[0])]
                if label in ['helmet', 'hat', 'headwear']:
                    found_helmet = True
        
        if found_helmet:
            st.success("✅ HELMET DETECTED. ENGINE STARTING...")
            st.balloons()
            if st.button("Reset System"):
                st.session_state.status = "START"
                st.rerun()
        else:
            st.error("❌ NO HELMET DETECTED. Ignition remains locked.")
            if st.button("Try Again"):
                st.rerun()