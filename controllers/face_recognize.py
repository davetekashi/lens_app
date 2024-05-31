import cv2
import dlib
import os
import numpy as np

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

# Capture video from the webcam
video_capture = cv2.VideoCapture(0)

while True:
    ret, frame = video_capture.read()
    if not ret:
        break
    
    # Recognize faces in the frame
    recognized_name = recognize_face(frame)
    
    # Display the results
    faces = detector(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY))
    for face in faces:
        x, y, w, h = face.left(), face.top(), face.width(), face.height()
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
        cv2.putText(frame, recognized_name, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

    cv2.imshow("Webcam Face Recognition", frame)
    
    # Break the loop on 'q' key press
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the webcam and close windows
video_capture.release()
cv2.destroyAllWindows()
