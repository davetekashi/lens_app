from fastapi import FastAPI, File, Form, UploadFile
from fastapi.responses import JSONResponse
from pymongo import MongoClient
from typing import List, Optional
import numpy as np
import gridfs
import dlib
import json
import cv2
import os
import ast


app = FastAPI()

# MongoDB connection string
connection_string = os.environ['DB_URL']
client = MongoClient(connection_string)
db = client["lensUser"]
# Initialize the MongoDB GridFS bucket
gfs = gridfs.GridFS(db)

# Recognition thresholds
threshold = 0.41

# Initialize dlib's face detector and face landmark predictor
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor(
    "models/shape_predictor_68_face_landmarks.dat")
face_rec_model = dlib.face_recognition_model_v1(
    "models/dlib_face_recognition_resnet_model_v1.dat")

# This function gets the face encoding or landmark of an image


def get_face_encodings(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    faces = detector(gray)
    if len(faces) == 0:
        return None

    face = faces[0]
    shape = predictor(gray, face)
    face_descriptor = face_rec_model.compute_face_descriptor(image, shape)
    return np.array(face_descriptor)

# This function stores a file to the database GridFS and returns the image_id


def store_images(files):
    image_ids = []
    for file in files:
        image_id = gfs.put(file.file, filename=file.filename)
        image_ids.append(image_id)

    return image_ids

# Get the images from the database for processing and attaching the face encoding to the images


def get_images_by_ids(image_ids):
    images = []
    for image_id in image_ids:
        grid_out = gfs.get(image_id)
        image_data = np.frombuffer(grid_out.read(), np.uint8)
        image = cv2.imdecode(image_data, cv2.IMREAD_COLOR)
        images.append(image)
    return images


def format_to_normal_array(string_array):
    normal_array = ast.literal_eval(string_array)
    return normal_array
# Define a function to get the encoding of 5 images and store to the databas


async def get_multiple_image_encoding(files: List[UploadFile], user_id: str, description: str):
    print("Getting multiple images")
    image_ids = store_images(files)
    images = get_images_by_ids(image_ids)
    encodings = []

    for image in images:
        encoding = get_face_encodings(image)
        encodings.append(encoding.tolist() if isinstance(
            encoding, np.ndarray) else encoding)

    # Update metadata of the stored images
    for image_id, encoding in zip(image_ids, encodings):
        db.fs.files.update_one(
            {"_id": image_id},
            {"$set": {"metadata": {
                "user_id": user_id,
                "description": description,
                "encodings": json.dumps(encoding)
            }}}
        )

    return image_ids
# Define a function to process a single image sent in for matching


# async def get_single_image_encoding(file: UploadFile) -> Optional[str]:
#     print('get_single_image_encoding')
#     image_data = np.frombuffer(file.file.read(), np.uint8)
#     image = cv2.imdecode(image_data, cv2.IMREAD_COLOR)
#     encoding = get_face_encodings(image)

#     if encoding is None:
#         return None

#     known_encodings = []
#     threshold = 0.6  # Adjust this threshold as needed

#     # Search for a match in the database
#     for grid_out in gfs.find():
#         if "encodings" in grid_out.metadata:
#             stored_encodings_str = grid_out.metadata["encodings"]
#             # print(stored_encodings_str)

#             # Convert JSON string back to array
#             stored_encodings = json.loads(stored_encodings_str)

#             for stored_encoding in stored_encodings:
#                 stored_encoding = np.array(stored_encoding)
#                 # Using 0.6 as the threshold for matching
#                 if np.linalg.norm(encoding - stored_encoding) < threshold:
#                     return grid_out.metadata["user_id"]

#     return None

async def get_single_image_encoding(file: UploadFile) -> Optional[str]:
    print('get_single_image_encoding')
    image_data = np.frombuffer(file.file.read(), np.uint8)
    image = cv2.imdecode(image_data, cv2.IMREAD_COLOR)
    encoding = get_face_encodings(image)

    if encoding is None or len(encoding) == 0:
        return None

    encoding = encoding[0]  # Ensure we are working with a single face encoding

    known_encodings = []

    # Search for a match in the database
    for grid_out in gfs.find():
        if "encodings" in grid_out.metadata:
            stored_encodings_str = grid_out.metadata["encodings"]

            # Convert JSON string back to array
            stored_encodings = json.loads(stored_encodings_str)

            for stored_encoding in stored_encodings:
                stored_encoding = np.array(stored_encoding)
                # Ensure the stored encoding has the correct shape
                if stored_encoding.shape == (128,):
                    known_encodings.append(
                        {"data": stored_encoding, "user": grid_out.metadata["user_id"]})

    if not known_encodings:
        return None

    # Convert list of known encodings to a numpy array for distance computation
    known_encoding_data = np.array([ke['data'] for ke in known_encodings])

    if known_encoding_data.size == 0:
        return None

    # Compute distances
    distances = np.linalg.norm(known_encoding_data - encoding, axis=1)
    min_distance_index = np.argmin(distances)
    if distances[min_distance_index] < 0.41:  # You can adjust this threshold
        return known_encodings[min_distance_index]["user"]

    return None

# ****** Routes ****** #

# Get the multiple images from the request form data


@app.post("/api/v1/register-user-lense-images")
async def register_user_lense_images(files: List[UploadFile] = File(...), user_id: str = Form(...), description: str = Form(...)):
    try:
        image_ids = await get_multiple_image_encoding(files, user_id, description)
        return JSONResponse(status_code=200, content={"message": "Files uploaded successfully", "image_ids": str(image_ids)})
    except Exception as e:
        print('Error processing user:', e)
        return JSONResponse(status_code=500, content={"message": "Error processing user"})

# Get the single image from the request form data


@app.post("/api/v1/recognize-user-lense-image")
async def recognize_user_lense_image(file: UploadFile = File(...)):
    try:
        user_id = await get_single_image_encoding(file)
        if user_id:
            return JSONResponse(status_code=200, content={"message": "User recognized", "user_id": user_id})
        else:
            return JSONResponse(status_code=404, content={"message": "User not recognized"})
    except Exception as e:
        print('Error processing user:', e)
        return JSONResponse(status_code=500, content={"message": "Error processing user"})

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8000)
