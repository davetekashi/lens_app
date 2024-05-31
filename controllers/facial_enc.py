import pymongo
import gridfs
from pymongo import MongoClient
import os
import cv2
import dlib
import numpy as np

# Connection string
connection_string = "mongodb+srv://100pay:100pay100pay@paylenscluster.pqefrnx.mongodb.net/?retryWrites=true&w=majority&appName=paylensCluster"

# Verify that the connection string is set
if not connection_string:
    raise ValueError("MONGODB_CONNECTION_STRING environment variable is not set")

# Connect to the MongoDB Atlas cluster
client = MongoClient(connection_string)

# Access the specific database
db = client["paylendb"]

# Create a GridFS instance
fs = gridfs.GridFS(db)

# Initialize dlib's face detector and face landmark predictor
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")
face_rec_model = dlib.face_recognition_model_v1("dlib_face_recognition_resnet_model_v1.dat")

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

def store_images(image_paths):
    """
    Store multiple images in GridFS and return their IDs.
    
    Parameters:
    - image_paths (list of str): List of file paths to the images.
    
    Returns:
    - list of ObjectId: List of GridFS file IDs.
    """
    image_ids = []
    face_encodings = []
    for image_path in image_paths:
        with open(image_path, 'rb') as f:
            image_id = fs.put(f, filename=os.path.basename(image_path))
            image_ids.append(image_id)
        
        # Compute face encodings
        image = cv2.imread(image_path)
        encoding = get_face_encodings(image)
        if encoding is not None:
            face_encodings.append(encoding.tolist())
    
    return image_ids, face_encodings

def create_user(user_info, image_paths):
    """
    Create a user document with user information and store images in GridFS.
    
    Parameters:
    - user_info (dict): Dictionary containing user details (name, account number, etc.).
    - image_paths (list of str): List of file paths to the user's images.
    """
    # Store images in GridFS and get the image IDs and face encodings
    image_ids, face_encodings = store_images(image_paths)
    
    # Add image IDs and face encodings to user information
    user_info['imageIds'] = image_ids
    user_info['faceEncodings'] = face_encodings
    
    # Insert user information into the collection
    collection = db["paylensCollection"]
    result = collection.insert_one(user_info)
    print(f"User {user_info['accountName']} created with ID: {result.inserted_id}")

# Example user information and images
users_data = [
    {
        "accountName": "Hogan Israel",
        "accountNumber": "123456789",
        "bankName": "Bank A",
        "bankCode": "001",
        "phoneNo": "123-456-7890",
        "email": "hogan.israel@gmail.com",
        "images": [
            "images/Hogan Israel/image10.jpeg",
            "images/Hogan Israel/image11.jpeg",
            "images/Hogan Israel/image12.jpeg",
            "images/Hogan Israel/image13.jpeg",
            "images/Hogan Israel/image14.jpeg"
        ]
    },
    {
        "accountName": "Ugomma Hilda",
        "accountNumber": "987654321",
        "bankName": "Bank B",
        "bankCode": "002",
        "phoneNo": "098-765-4321",
        "email": "ugomma.hilda@example.com",
        "images": [
            "images/Ugomma Hilda-20240529T034919Z-001/image20 (1).jpeg",
            "images/Ugomma Hilda-20240529T034919Z-001/image21.jpeg",
            "images/Ugomma Hilda-20240529T034919Z-001/image22 (1).jpeg",
            "images/Ugomma Hilda-20240529T034919Z-001/image23 (1).jpeg",
            "images/Ugomma Hilda-20240529T034919Z-001/image24.jpeg"
        ]
    }
]

# Store user information and images
for user in users_data:
    user_info = {
        "accountName": user["accountName"],
        "accountNumber": user["accountNumber"],
        "bankName": user["bankName"],
        "bankCode": user["bankCode"],
        "phoneNo": user["phoneNo"],
        "email": user["email"]
    }
    image_paths = user["images"]
    create_user(user_info, image_paths)
