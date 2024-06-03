import cv2
import dlib
import os
import numpy as np

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

# Specify the person's name
person_name = "Hogan Israel"  # Replace with the person's name

# Directory containing the person's images
person_folder = os.path.join("images", person_name)

# Check if the directory exists
if not os.path.isdir(person_folder):
    print(f"Directory for {person_name} not found.")
    exit()

# Initialize list to store face encodings
encodings = []

# Iterate through the images in the person's directory
for image_name in os.listdir(person_folder):
    image_path = os.path.join(person_folder, image_name)
    image = cv2.imread(image_path)
    if image is None:
        continue

    encoding = get_face_encodings(image)
    if encoding is not None:
        encodings.append(encoding)
        print(f"Encoding for {image_name}: {encoding}")
    else:
        print(f"No face found in {image_name}")

# Calculate and print the average encoding
#
# #if encodings:
   # average_encoding = np.mean(encodings, axis=0)
    #print(f"Average encoding for {person_name}: {average_encoding}")
#else:
 #   print(f"No encodings found for {person_name}")

