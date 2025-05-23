import firebase_admin
from firebase_admin import credentials, firestore

# Initialize Firebase app
cred = credentials.Certificate("-")
firebase_admin.initialize_app(cred)

# Firestore client
db = firestore.client()

def add_data(collection, document_id, data):
    """Add data to Firestore."""
    db.collection(collection).document(document_id).set(data)
