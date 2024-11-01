from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from pymongo import MongoClient
from datetime import datetime
from bson import ObjectId
from ..firebase import add_data  # Ensure this points to the correct Firebase function import

# Initialize the router
router = APIRouter()

# MongoDB setup
client = MongoClient("mongodb://localhost:27017/")
db = client["secure_chrome_extension"]
reports_collection = db["reports"]

# Define a Pydantic model for the report request body
class Report(BaseModel):
    url: str
    description: str

def serialize_report(report):
    """Serialize the MongoDB report document to JSON format."""
    return {
        "id": str(report["_id"]),
        "url": report["url"],
        "description": report["description"],
        "timestamp": report["timestamp"]
    }

@router.post("/report")
async def report(report: Report):
    try:
        report_data = report.dict()
        report_data["timestamp"] = datetime.utcnow()  # Add a timestamp field to the report

        # MongoDB insertion with error handling
        try:
            result = reports_collection.insert_one(report_data)
            print(f"Inserted into MongoDB with ID: {result.inserted_id}")
        except Exception as mongo_err:
            print(f"MongoDB insertion error: {mongo_err}")
            raise HTTPException(status_code=500, detail="Error inserting report into MongoDB")

        # Prepare data for Firebase and handle potential Firebase errors
        firestore_data = {
            "url": report.url,
            "description": report.description,
            "timestamp": report_data["timestamp"]
        }
        try:
            add_data("reports", str(result.inserted_id), firestore_data)
            print(f"Added to Firebase with ID: {result.inserted_id}")
        except Exception as firebase_err:
            print(f"Firebase insertion error: {firebase_err}")
            raise HTTPException(status_code=500, detail="Error inserting report into Firebase")

        # Retrieve the inserted report for response
        inserted_report = reports_collection.find_one({"_id": result.inserted_id})
        if inserted_report:
            return {"message": "Report submitted successfully", "report": serialize_report(inserted_report)}
        else:
            raise HTTPException(status_code=404, detail="Report not found in MongoDB after insertion")

    except Exception as e:
        print(f"Error occurred: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
