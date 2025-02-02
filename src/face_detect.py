import requests
import cv2
import os
import time
from picamera2 import Picamera2

# Flask server URL
SERVER_URL = "http://192.168.6.105:5000/upload-photo"
room = "127a"

# Initialize camera
picam2 = Picamera2()
picam2.configure(picam2.create_still_configuration(main={"format": 'XRGB8888', "size": (640, 480)}))
picam2.start()

# Load face detector
face_cascade = cv2.CascadeClassifier('/usr/share/opencv4/haarcascades/haarcascade_frontalface_default.xml')

def capture_and_send():
    while True:
        # Capture image
        image = picam2.capture_array()
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=10, minSize=(30, 30))

        if len(faces) > 0:
            image_path = time.strftime("%Y%m%d-%H%M%S.jpg")
            cv2.imwrite(image_path, image)

            # Send image to Flask server
            with open(image_path, "rb") as img_file:
                files = {"image": img_file,
                         "room": room,
                         "date" : time.strftime("%Y%m%d"),
                         "time" : time.strftime("%H%M%S")}
                response = requests.post(SERVER_URL, files=files)
                
                if response.status_code == 200:
                    print("Response:", response.json())
                else:
                    print("Failed to send image:", response.text)
        
        time.sleep(1)  # Adjust frequency as needed

if __name__ == "__main__":
    capture_and_send()