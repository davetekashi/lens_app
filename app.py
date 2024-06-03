import cv2
import dlib
import os
import numpy as np
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from typing import List
import logging

app = FastAPI()

# Paths to the model files
shape_predictor_path = "shape_predictor_68_face_landmarks.dat"
face_rec_model_path = "dlib_face_recognition_resnet_model_v1.dat"

# Initialize dlib's face detector and face landmark predictor
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor(shape_predictor_path)
face_rec_model = dlib.face_recognition_model_v1(face_rec_model_path)

# Function to compute the 128D face encoding for an image
def get_face_encodings(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    faces = detector(gray)
    if len(faces) == 0:
        return None

    face = faces[0]
    shape = predictor(gray, face)
    face_descriptor = face_rec_model.compute_face_descriptor(image, shape)
    return np.array(face_descriptor)

# Load images and labels
image_folder = "images"
known_encodings = []
known_labels = []

for person_name in os.listdir(image_folder):
    person_folder = os.path.join(image_folder, person_name)
    if not os.path.isdir(person_folder):
        continue
    
    for image_name in os.listdir(person_folder):
        image_path = os.path.join(person_folder, image_name)
        image = cv2.imread(image_path)
        if image is None:
            continue
        
        encoding = get_face_encodings(image)
        if encoding is not None:
            known_encodings.append(encoding)
            known_labels.append(person_name)

# Function to recognize face in a given image
def recognize_face(image):
    unknown_encoding = get_face_encodings(image)
    if unknown_encoding is None:
        return "Unknown"
    
    distances = np.linalg.norm(known_encodings - unknown_encoding, axis=1)
    min_distance_index = np.argmin(distances)
    if distances[min_distance_index] < 0.41:  # You can adjust this threshold
        return known_labels[min_distance_index]
    else:
        return "Unknown"
    
    





# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.get("/")
def read_root():
    return {"message": "Face Recognition API is running. Use the /recognize/ endpoint to upload an image."}

@app.post("/recognize/")
async def recognize(file: UploadFile = File(...)):
    contents = await file.read()
    logger.info("File received")
    np_arr = np.frombuffer(contents, np.uint8)
    image = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
    
    recognized_name = recognize_face(image)
    logger.info(f"Recognized: {recognized_name}")
    return JSONResponse(content={"recognized_name": recognized_name})


# To run the app, use: uvicorn app:app --reload
