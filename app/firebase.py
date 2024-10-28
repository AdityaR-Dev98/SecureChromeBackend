import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

# Path to your service account key
cred = credentials.Certificate("C:\\Users\\rasto\\Downloads\\SecureChromeBackend\\keys\\chromeextension-ba7af-firebase-adminsdk-4wllh-24e73f6b60.json")  # Update the path

# Initialize the Firebase app
firebase_admin.initialize_app(cred)

# Initialize Firestore
db = firestore.client()  # Initialize Firestore

# Example usage function to add data to Firestore
def add_data(collection, document_id, data):
    """Add data to Firestore."""
    db.collection(collection).document(document_id).set(data)