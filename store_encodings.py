import cv2
import dlib
import numpy as np
from pymongo import MongoClient
import gridfs

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

# Retrieve all users
users = users_collection.find()


# Iterate through each user and compute encodings for their images
for user in users:
    print(user)
    user_id = user["_id"]
    image_encodings = []
    if "image_ids" in user:
        for image_id in user["image_ids"]:
            image_data = fs.get(image_id).read()
            np_arr = np.frombuffer(image_data, np.uint8)
            image = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
            encoding = get_face_encodings(image)
            if encoding is not None:
                image_encodings.append(encoding.tolist())
                print(f"Computed encoding for image ID: {image_id}")
    
    # Store the encodings in the user document
    if image_encodings:
        users_collection.update_one(
            {"_id": user_id},
            {"$set": {"image_encodings": image_encodings}}
        )
        print(f"Updated user {user_id} with encodings")

print("Finished computing and storing encodings")
