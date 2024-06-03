import cv2
import dlib
import numpy as np
from pymongo import MongoClient
import gridfs


# MongoDB Atlas connection
connection_string = "mongodb+srv://badboiDave:badboi4life@cluster0.d4bcj27.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(connection_string)
db = client["paylens_db"]
users_collection = db["paylens_collection"]
fs = gridfs.GridFS(db)


users = users_collection.find()

for user in users:
    print (user['image_encodings'][0])

