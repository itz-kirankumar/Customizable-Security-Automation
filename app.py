import cv2
import streamlit as st
import numpy as np
import pandas as pd
from ultralytics import YOLO
# import pygame
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from twilio.rest import Client
import geocoder
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime
import time
# pygame.mixer.init()


# Load the pre-trained YOLOv8 model using Ultralytics
model = YOLO('best.pt')

# Set up Streamlit layout
st.set_page_config(
    page_title="Customizable Security Automation",
    page_icon="shield.png",
    layout="wide"
)


# Streamlit UI
st.title('Customizable Security Automation')
st.sidebar.title("Real-time Detection")
st.sidebar.title('Settings')

# Initialize privacy_mode_enabled and privacy_timer_end as False and None respectively
privacy_mode_enabled = False
privacy_timer_end = None

# Add a checkbox for Privacy Mode
if not privacy_mode_enabled:
    privacy_mode_enabled = st.sidebar.checkbox("Privacy Mode")

# Check for Privacy Mode timer
if privacy_mode_enabled:
    if privacy_timer_end is None or datetime.datetime.now() > privacy_timer_end:
        privacy_timer_minutes = st.sidebar.number_input("Set Privacy Mode Timer (minutes)", min_value=1)
        # Calculate the timer end time
        privacy_timer_end = datetime.datetime.now() + datetime.timedelta(minutes=privacy_timer_minutes)

confidence_threshold = st.sidebar.slider('Confidence Threshold', min_value=0.0, max_value=1.0, value=0.5)
override_threshold = st.sidebar.slider('Override Threshold', min_value=0.0, max_value=1.0, value=0.5)




st.sidebar.title('Alert Notifications')

# Create checkboxes for alerts
enable_text_alert = st.sidebar.checkbox("Text Alert")
# enable_sound_alert = st.sidebar.checkbox("Sound Alert")
enable_sms_alert = st.sidebar.checkbox("SMS Alert")
enable_email_alert = st.sidebar.checkbox("Email Alert")
recipient_phone = st.sidebar.text_input('Enter Mobile Number')
if not recipient_phone:
        st.sidebar.warning("Please enter your mobile number.")
        # st.stop()

recipient_email = st.sidebar.text_input('Enter Email')
if not recipient_email:
        st.sidebar.warning("Please enter your e-mail address.")
        # st.stop()

    




# Usage
image_path = 'alert_image.jpg'


# Alert sound file
alert_sound = 'alert.wav'

# Main content
# use_webcam = st.checkbox('Use Webcam')
use_ipcam = st.checkbox('Use IP cam')

if use_ipcam:
    ipcam_address = st.text_input('Enter IP Camera Address')
    if not ipcam_address:
        st.warning("Please enter the IP camera address.")
        st.stop()  # Stop execution until an address is provided
    st.write("IP Camera Stream:")
    stframe = st.empty()
    cap = cv2.VideoCapture(ipcam_address)

# elif use_webcam:
#     st.write("Webcam Detection:")
#     stframe = st.empty()
#     cap = cv2.VideoCapture(0)
else:
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

# List of available object classes
class_list = ["deer","elephant","fire","human","tiger"]


# Multi-select widget for object classes3r
# selected_classes = st.sidebar.multiselect("Customize your security system", class_list, default=class_list)
selected_classes_day = st.sidebar.multiselect("Daytime Classes", class_list, default=class_list)
selected_classes_night = st.sidebar.multiselect("Nighttime Classes", class_list, default=class_list)

# Add time range inputs
day_start_time = st.sidebar.time_input("Day Start Time", datetime.time(6, 0))
day_end_time = st.sidebar.time_input("Day End Time", datetime.time(18, 0))
night_start_time = st.sidebar.time_input("Night Start Time", datetime.time(18, 0))
night_end_time = st.sidebar.time_input("Night End Time", datetime.time(6, 0))

def is_daytime():
    now = datetime.datetime.now().time()
    
    if day_start_time <= now <= day_end_time:
        return True
    elif night_start_time <= now or now <= night_end_time:
        return False
    else:
        return True 


def send_email(subject, message, image_path, recipient_email):
    from_email = 'projectbyteamzero@gmail.com'
    from_password = 'bzfb pdsp svwq sbbp'

    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = recipient_email
    msg['Subject'] = subject

    # Attach the message
    msg.attach(MIMEText(message, 'plain'))

    # Attach the image
    with open(image_path, 'rb') as img_file:
        image = MIMEImage(img_file.read())
        msg.attach(image)

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(from_email, from_password)
    text = msg.as_string()
    server.sendmail(from_email, recipient_email, text)
    server.quit()


# git SMS Alerts using Twilio (example)


def send_sms(message, recipient_phone_number):
    account_sid = 'ACe9358dd8fb0bf3ca2c95db6a42c5aaa9'
    auth_token = 'ff77f6220676e07c05299b4864139177'

    client = Client(account_sid, auth_token)

    message = client.messages.create(
        body=message,
        from_='+19208802985',  # Your Twilio phone number
        to=recipient_phone_number
    )

def get_current_location(latitude, longitude):
    try:
        # Fetch GPS coordinates using the device's default method (usually GPS)
        location = geocoder.ip('me')

        # Check if location was successfully fetched
        if location.ok:
            latitude = location.lat
            longitude = location.lng
            maps_link = f"https://www.google.com/maps/search/?api=1&query={latitude},{longitude}"
            return maps_link
        else:
            print("Unable to fetch location.")
            return None
    except Exception as e:
        print(f"Error fetching location: {e}")
        return None

     
latitude = 12.9716  # Example latitude for New Delhi, India
longitude = 77.5946  # Example longitude for New Delhi, India

location_info = get_current_location(latitude,longitude)
print(location_info)


# Database
Base = declarative_base()
class Alert(Base):
    __tablename__ = 'alerts'

    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime)
    object_class = Column(String)
    confidence = Column(Float)
    location = Column(String)

# Initialize the SQLite database
engine = create_engine('sqlite:///alerts.db')
Base.metadata.create_all(engine)

# Create a session to interact with the database
Session = sessionmaker(bind=engine)
session = Session()

# Initialize an empty list for results
results = []

while cap is not None and cap.isOpened():
    ret, frame = cap.read()
    
    if ret:
        frame = cv2.resize(frame, (640, 480))

        if not privacy_mode_enabled or datetime.datetime.now() > privacy_timer_end:
            if is_daytime():
                if day_start_time <= datetime.datetime.now().time() <= day_end_time:
                    results = model.predict(frame)
            else:
                if night_start_time <= datetime.datetime.now().time() or datetime.datetime.now().time() <= night_end_time:
                    results = model.predict(frame)
            
            if results:
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

                    if c.lower() in (selected_classes_day if is_daytime() else selected_classes_night):
                        if row[4] >= override_threshold:
                            
                            cv2.imwrite('alert_image.jpg',frame)

                            if enable_text_alert:
                                st.warning(f"ALERT: Object Detected - {c}")
                        
                            if enable_email_alert:
                            
                                if not recipient_email:
                                    st.warning("Please enter your e-mail address.")
                                    st.stop()
                            
                                send_email(f"ALERT: Object Detected - {c}", f"Object Detected - {c} at {location_info}", image_path, recipient_email)

                            if enable_sms_alert:
                                
                                if not recipient_phone:
                                    st.warning("Please enter your mobile number.")
                                    st.stop()
                                # send_sms(f"ALERT: Object Detected - {c} at {location_info}", recipient_phone)

                            # if enable_sound_alert:
                            #     pygame.mixer.music.load(alert_sound)
                            #     pygame.mixer.music.play()

                            

                            timestamp = datetime.datetime.now() 
                            
                            new_alert = Alert(timestamp=timestamp, object_class=c, confidence=row[4], location=location_info)
                            session.add(new_alert)
                            session.commit()
                            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                            stframe.image(frame, channels='RGB', use_column_width=True)

    else:
        break

if cap is not None:
    cap.release()

st.subheader("Historical Alerts")
show_alerts = st.button("Show Historical Alerts")

# Create a radio button for sorting
sorting_option = st.radio("Sort Alerts By:", ("Older to Newer", "Newer to Older"))

if show_alerts:
    
    # Fetch the alerts from the database based on sorting option
    if sorting_option == "Older to Newer":
        alerts = session.query(Alert).order_by(Alert.timestamp).all()
    else:
        alerts = session.query(Alert).order_by(Alert.timestamp.desc()).all()

    if alerts:
        for alert in alerts:
            st.write(f"Timestamp: {alert.timestamp}, Object Class: {alert.object_class}, Confidence: {alert.confidence}, Location: {alert.location}")
    else:
        st.write("No historical alerts found.")


