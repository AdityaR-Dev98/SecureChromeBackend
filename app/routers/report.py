from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import datetime
from bson.objectid import ObjectId
from app.models.db import db  # Import database instance from db.py
from ..firebase import add_data
from .update_model import update_prediction_based_on_reports
from app.utils.utils import extract_url_features
from app.routers.scan import scan  # Import scan logic to fetch current predictions


# Define the report schema
class Report(BaseModel):
    url: str
    description: str
    user_id: str

# Helper function to serialize MongoDB documents
def serialize_report(report):
    return {
        "id": str(report["_id"]),
        "url": report["url"],
        "description": report["description"],
        "timestamp": report["timestamp"],
        "user_id": report["user_id"]
    }

# Router instance
router = APIRouter()

@router.post("/report")
async def report(report: Report):
    try:
        report_data = report.dict()
        report_data["timestamp"] = datetime.utcnow()

        # Check if the user already reported this URL
        existing_report = await db["reports"].find_one({"url": report.url, "user_id": report.user_id})
        if existing_report:
            raise HTTPException(status_code=400, detail="You have already reported this website.")

        # Get the current prediction for the URL
        scan_response = await scan(report.url)
        current_prediction = scan_response["prediction"]

        # Check if the report contradicts the current prediction
        report_is_opposite = (
            (current_prediction == "Safe" and "malicious" in report.description.lower()) or
            (current_prediction == "Malicious" and "safe" in report.description.lower())
        )

        # Insert the report into MongoDB
        result = await db["reports"].insert_one(report_data)
        report_id = result.inserted_id

        # Add the data to Firebase
        firestore_data = {
            "url": report.url,
            "description": report.description,
            "timestamp": report_data["timestamp"]
        }
        add_data("reports", str(report_id), firestore_data)

        # Count reports for the URL
        report_count = await db["reports"].count_documents({"url": report.url})

        # If contradictions exceed threshold (e.g., 10 reports), update the prediction
        if report_is_opposite and report_count >= 10:
            await update_prediction_based_on_reports(report.url)

        inserted_report = await db["reports"].find_one({"_id": report_id})
        return {"message": "Report submitted successfully", "report": serialize_report(inserted_report)}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
