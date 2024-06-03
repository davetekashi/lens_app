from pymongo import MongoClient
from bson import ObjectId
import gridfs
import os



# MongoDB Atlas connection
connection_string = "mongodb+srv://badboiDave:badboi4life@cluster0.d4bcj27.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(connection_string)
db = client["paylens_db"]
users_collection = db["paylens_collection"]
fs = gridfs.GridFS(db)

# Sample users data
users_data = [
    {
        "account_name": "Rita London",
        "account_number": "123456789",
        "bank_name": "Access Bank",
        "bank_code": "001",
        "phone_number": "+1234567890",
        "email": "Ritalondon@gmail.com",
        "image_paths": [
            r"C:\Users\USER\PycharmProjects\Lens app\images\Rita London\image15.jpeg",
            r"C:\Users\USER\PycharmProjects\Lens app\images\Rita London\image17.jpeg",
            r"C:\Users\USER\PycharmProjects\Lens app\images\Rita London\image18.jpeg",
            r"C:\Users\USER\PycharmProjects\Lens app\images\Rita London\image19.jpeg",
            r"C:\Users\USER\PycharmProjects\Lens app\images\Rita London\Rita1.jpeg"
        ]
    },
    {
        "account_name": "Hogan Isreal ",
        "account_number": "987654321",
        "bank_name": "First Bank",
        "bank_code": "002",
        "phone_number": "+0987654321",
        "email": "Hoganisreal@gmail.com",
        "image_paths": [
            r"C:\Users\USER\PycharmProjects\Lens app\images\Hogan Israel\image10.jpeg",
            r"C:\Users\USER\PycharmProjects\Lens app\images\Hogan Israel\image11.jpeg",
            r"C:\Users\USER\PycharmProjects\Lens app\images\Hogan Israel\image12.jpeg",
            r"C:\Users\USER\PycharmProjects\Lens app\images\Hogan Israel\image13.jpeg",
            r"C:\Users\USER\PycharmProjects\Lens app\images\Hogan Israel\image14.jpeg"
        ]
    },
    {
        "account_name": "Legacy",
        "account_number": "112233445",
        "bank_name": "Diamond bank",
        "bank_code": "003",
        "phone_number": "+1234567890",
        "email": "agacyinc@gmail.com",
        "image_paths": [
            r"C:\Users\USER\PycharmProjects\Lens app\images\Legacy\image5.jpeg",
            r"C:\Users\USER\PycharmProjects\Lens app\images\Legacy\image6.jpeg",
            r"C:\Users\USER\PycharmProjects\Lens app\images\Legacy\image7.jpeg",
            r"C:\Users\USER\PycharmProjects\Lens app\images\Legacy\image8.jpeg",
            r"C:\Users\USER\PycharmProjects\Lens app\images\Legacy\image9.jpeg"
        ]
    }
]

# Function to store user data and images
def store_user_data(user_data):
    # Insert user data into MongoDB
    user_id = users_collection.insert_one({
        "account_name": user_data["account_name"],
        "account_number": user_data["account_number"],
        "bank_name": user_data["bank_name"],
        "bank_code": user_data["bank_code"],
        "phone_number": user_data["phone_number"],
        "email": user_data["email"],
    }).inserted_id
    print(f"Inserted user with ID: {user_id}")

    # Store images in GridFS and link to user document
    image_ids = []
    for image_path in user_data["image_paths"]:
        with open(image_path, "rb") as f:
            image_id = fs.put(f, filename=os.path.basename(image_path), user_id=user_id)
            image_ids.append(image_id)
            print(f"Stored image {image_path} with ID: {image_id}")

    # Update user document with image IDs
    users_collection.update_one(
        {"_id": user_id},
        {"$set": {"image_ids": image_ids}}
    )

    print(f"Updated user document with image IDs for user {user_data['account_name']}")

# Store data for all users
for user_data in users_data:
    store_user_data(user_data)

