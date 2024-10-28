from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pymongo import MongoClient
from bson import ObjectId
from .firebase import add_data  # Import the add_data function from firebase.py
from datetime import datetime  # Import datetime for timestamps

# MongoDB setup
client = MongoClient("mongodb://localhost:27017/")
db = client["secure_chrome_extension"]
reports_collection = db["reports"]

app = FastAPI()

# CORS middleware setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (or specify your extension's origin)
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

class Report(BaseModel):
    url: str
    description: str

class ScanRequest(BaseModel):
    url: str

def serialize_report(report):
    """Convert MongoDB report document to a serializable format."""
    return {
        "id": str(report["_id"]),  # Convert ObjectId to string
        "url": report["url"],
        "description": report["description"]
    }

@app.post("/report")
async def report(report: Report):
    try:
        # Insert the report into MongoDB
        report_data = report.dict()
        result = reports_collection.insert_one(report_data)
        
        # Prepare data to send to Firestore
        firestore_data = {
            "url": report.url,
            "description": report.description,
            "timestamp": datetime.utcnow()  # Include a timestamp if needed
        }
        
        # Add data to Firestore
        add_data("reports", str(result.inserted_id), firestore_data)  # Use the MongoDB ID as the document ID

        # Retrieve the inserted report document
        inserted_report = reports_collection.find_one({"_id": result.inserted_id})
        return {"message": "Report submitted successfully", "report": serialize_report(inserted_report)}
    except Exception as e:
        print(f"Error occurred: {e}")  # Print the error for debugging
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.post("/scan")
async def scan(scan_request: ScanRequest):
    url = scan_request.url
    # Implement your scanning logic here
    result = {"url": url, "status": "No threats detected"}
    return result

@app.post("/update-model")
async def update_model():
    # Placeholder for model update logic
    return {"message": "Model update triggered (logic to be implemented)"}
