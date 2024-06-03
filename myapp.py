import cv2
import dlib
import numpy as np
from pymongo import MongoClient
import gridfs
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from typing import List

# Initialize FastAPI
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

# MongoDB Atlas connection
connection_string = "mongodb+srv://badboiDave:badboi4life@cluster0.d4bcj27.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(connection_string)
db = client["paylens_db"]
users_collection = db["paylens_collection"]
fs = gridfs.GridFS(db)



@app.post("/recognize/")
async def recognize_face(file: UploadFile = File(...)):
    try:
        # Read the uploaded image
        image_data = await file.read()
        np_arr = np.frombuffer(image_data, np.uint8)
        image = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
        
        # Get the face encoding for the uploaded image
        unknown_encoding = get_face_encodings(image)
        if unknown_encoding is None:
            raise HTTPException(status_code=400, detail="No face detected in the image")

        # Retrieve all users from the database
        users = users_collection.find()

        # Iterate through each user and compare encodings
        for user in users:
            if "image_encodings" in user:
                for encoding in user["image_encodings"]:
                    known_encoding = encoding    #np.array
                    distance = np.linalg.norm(known_encoding - unknown_encoding)
                    if distance < 0.41:  
                        # Return user details
                        user_info = {
                            "account_name": user["account_name"],
                            "account_number": user["account_number"],
                            "bank_name": user["bank_name"],
                            "bank_code": user["bank_code"],
                            "phone_number": user["phone_number"],
                            "email": user["email"],
                        }
                        return JSONResponse(content=user_info)

        # If no match is found
        raise HTTPException(status_code=404, detail="No matching user found")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    return {"message": "Face Recognition API is running. Use the /recognize/ endpoint to upload an image."}
