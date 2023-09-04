import cv2
import streamlit as st
import numpy as np
import pandas as pd
from ultralytics import YOLO

# Load the pre-trained YOLOv8 model using Ultralytics
model = YOLO('best.pt')

# Set up Streamlit layout
st.set_page_config(
    page_title="Wildlife Security System",
    page_icon="🦁",
    layout="wide"
)

# Streamlit UI
st.title('Wildlife Security System')
st.sidebar.title("Real-time Detection")
st.sidebar.title('Settings')
confidence_threshold = st.sidebar.slider('Confidence Threshold', min_value=0.0, max_value=1.0, value=0.5)
override_threshold = st.sidebar.slider('Override Threshold', min_value=0.0, max_value=1.0, value=0.5)

# Main content
st.write("Upload a video for detection:")
uploaded_file = st.file_uploader("Choose a file...", type=["mp4", "mov", "avi"])
stframe = st.empty()
cap = None

if uploaded_file is not None:
    file_extension = uploaded_file.name.split('.')[-1]
    if file_extension in ['jpg', 'png']:
        image = np.array(uploaded_file)
        stframe.image(image, channels="RGB", use_column_width=True)
    elif file_extension in ['mp4', 'mov', 'avi']:
        # Save the uploaded video to a temporary file
        with open('temp_video.mp4', 'wb') as temp_file:
            temp_file.write(uploaded_file.read())
        cap = cv2.VideoCapture('temp_video.mp4')

class_list = ["bear", "cat", "cheetah", "cow", "dog", "elephant", "fire", "goat", "hen", "horse", "human", "lion",
              "monkey", "panda", "rhino", "tiger", "zebra"]

while cap is not None and cap.isOpened():
    ret, frame = cap.read()

    if ret:
        frame = cv2.resize(frame, (640, 480))

        results = model.predict(frame)
        a = results[0].boxes.data
        px = pd.DataFrame(a).astype("float")

        for index, row in px.iterrows():
            x1 = int(row[0])
            y1 = int(row[1])
            x2 = int(row[2])
            y2 = int(row[3])
            d = int(row[5])
            c = class_list[d]

            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(frame, str(c), (x1, y1), cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 0, 0), 1)

            if c.lower() in ["bear", "cheetah", "elephant", "fire", "lion", "panda", "rhino", "tiger"]:
                if row[4] >= override_threshold:
                    # Trigger an alert mechanism (print a message for demonstration)
                    st.warning(f"ALERT: Object Detected - {c}")

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        stframe.image(frame, channels='RGB', use_column_width=True)

    else:
        break

if cap is not None:
    cap.release()
