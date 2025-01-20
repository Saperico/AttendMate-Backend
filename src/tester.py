#!/usr/bin/env python3
# -- Facial Recogntiion and comparison module -- 
import cv2
import os
import numpy as np
from datetime import date

# Initialize regognizer
# copy this code over to other parts 

# store index and name

class Trainer():
    def __init__(self):
        people = []
    def train_recognizer(self, nameIndex, name):
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        recognizer = cv2.face.LBPHFaceRecognizer_create()  # This works after installing opencv-contrib-python
        images = []
        labels = []
        label = nameIndex  
        self.people.append((nameIndex,name)) # add to tuple index and name 

        # CHANGE THIS TO YOUR TRIANING FILES 
        # modify later to detect multiple people or use multiple training yml files instead
        images_path = 'C:/Users/ccamn/Desktop/Facial recognition/Faces'

        print(f"Training recognizer using images from: {images_path}")

        # Loop over all images in the folder
        for image_filename in os.listdir(images_path):
            img_path = os.path.join(images_path, image_filename)
            img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)

            if img is None:
                print(f"Error loading image: {img_path}")
                continue
            
            print(f"Loaded image: {img_path}")  # VERBOSE check
            
            # Detect faces in the image
            faces = face_cascade.detectMultiScale(img, scaleFactor=1.1, minNeighbors=10, minSize=(30, 30))

            if len(faces) == 0:
                print(f"No faces detected in {img_path}")
            else:
                print(f"Faces detected in {img_path}: {len(faces)}")

            for (x, y, w, h) in faces:
                roi_gray = img[y:y+h, x:x+w]
                images.append(roi_gray)
                labels.append(label)

        # if images were loaded and faces were detected
        if len(images) > 0:
            print(f"Training with {len(images)} face images.")
            # Train the recognizer
            recognizer.train(images, np.array(labels))
            recognizer.save('C:/Users/ccamn/Desktop/Facial recognition/face_recognizer.yml')  # Save the trained model
            print("Model saved successfully!")
        else:
            print("No faces detected for training.")

    def Checkface(self, imgSrc): 
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        recognizer = cv2.face.LBPHFaceRecognizer_create()  # This works after installing opencv-contrib-python
        # Load the trained recognizer (for future use)
        recognizer.read('C:/Users/ccamn/Desktop/Facial recognition/face_recognizer.yml')
        print("Recognizer model loaded.")
        # Load a test image (frame from a video feed example)
        image_path = imgSrc  # Provide the path to your image
        print(f"Loading test image from: {image_path}")
        image = cv2.imread(image_path)


        # Convert the image to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        print("Converted image to grayscale.")

        # Detect faces in the image
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=10, minSize=(30, 30), flags=cv2.CASCADE_SCALE_IMAGE)
        print(f"Detected {len(faces)} face(s) in the test image.")

        # Define the threshold for unknown recognition (confidence score for identification)
        THRESHOLD = 65  # Adjust this value to be stricter (higher)
        print(f"Using threshold value: {THRESHOLD}")

        # Loop over the detected faces
        for (x, y, w, h) in faces:
            # Draw rectangle around the face
            cv2.rectangle(image, (x, y), (x + w, y + h), (255, 0, 0), 2)
            print(f"Detected face at: x={x}, y={y}, w={w}, h={h}")

            # Extract face region and predict the label
            roi_gray = gray[y:y + h, x:x + w]
            label, confidence = recognizer.predict(roi_gray)
            print(f"Predicted label: {label}, Confidence: {confidence}")

            # Check if the confidence is less than person
            if confidence < THRESHOLD:
                nameIndex, name = self.people[int(label) - 1]  # Unpack the tuple
                print(f"Face recognized as person {name} (Confidence: {confidence})")
                cv2.putText(image, f"{name}", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
                # UPDATE JOE BIDEN BY SQL ATTENDANCE FOR TODAY
                # code here to link to sql

            else:
                print(f"Face marked as Unknown (Confidence: {confidence})")
                cv2.putText(image, "Unknown", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)

        # Dispalying the result is useless as a functionality and only useful for tesitng
        # commented out for release
        # Display the result
        #cv2.imshow('Face Detection and Recognition', image)
        
        # await keypress
        #print("Press any key to close the image window.")
        #cv2.waitKey(0)
        #cv2.destroyAllWindows()
# Call the training function for our training model for a person and index
#x = Trainer()
#x.train_recognizer(1, "joe biden")  # joe biden is index 1




