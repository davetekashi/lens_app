# fastapi_server.py

from fastapi import FastAPI, File, Form, UploadFile
from fastapi.responses import JSONResponse
import pymongo
import gridfs
from pymongo import MongoClient
import os
import numpy as np
import cv2
import dlib

app = FastAPI()

# MongoDB connection string
connection_string = "mongodb+srv://100pay:100pay100pay@paylenscluster.pqefrnx.mongodb.net/?retryWrites=true&w=majority&appName=paylensCluster"
client = MongoClient(connection_string)
db = client["paylendb"]
fs = gridfs.GridFS(db)

# Initialize dlib's face detector and face landmark predictor
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")
face_rec_model = dlib.face_recognition_model_v1("dlib_face_recognition_resnet_model_v1.dat")

def get_face_encodings(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    faces = detector(gray)
    if len(faces) == 0:
        return None
    face = faces[0]
    shape = predictor(gray, face)
    face_descriptor = face_rec_model.compute_face_descriptor(image, shape)
    return np.array(face_descriptor)

def store_images(files):
    image_ids = []
    for file in files:
        image_id = fs.put(file.file, filename=file.filename)
        image_ids.append(image_id)
    return image_ids

@app.post("/process_user")
async def process_user(accountName: str = Form(...), accountNumber: str = Form(...), bankName: str = Form(...),
                       bankCode: str = Form(...), phoneNo: str = Form(...), email: str = Form(...),
                       files: list[UploadFile] = File(...)):
    user_info = {
        "accountName": accountName,
        "accountNumber": accountNumber,
        "bankName": bankName,
        "bankCode": bankCode,
        "phoneNo": phoneNo,
        "email": email
    }
    
    # Store images in GridFS and get the image IDs
    image_ids = store_images(files)
    
    # Add image IDs to user information
    user_info['imageIds'] = image_ids

    # Insert user information into the collection
    collection = db["paylensCollection"]
    result = collection.insert_one(user_info)
    
    return JSONResponse(content={"message": f"User {accountName} created with ID: {result.inserted_id}"})

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8000)