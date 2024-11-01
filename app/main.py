from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pymongo import MongoClient
from bson import ObjectId
from .firebase import add_data
from datetime import datetime
import joblib
import numpy as np
import pandas as pd

# MongoDB setup
client = MongoClient("mongodb://localhost:27017/")
db = client["secure_chrome_extension"]
reports_collection = db["reports"]

# Load the trained model pipeline (includes preprocessor and classifier)
model_pipeline = joblib.load('C:\\Users\\rasto\\Downloads\\SecureChromeBackend\\random_forest_pipeline.pkl')

# Initialize FastAPI app
app = FastAPI()

# CORS middleware setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Report(BaseModel):
    url: str
    description: str

class ScanRequest(BaseModel):
    url: str

def serialize_report(report):
    return {
        "id": str(report["_id"]),
        "url": report["url"],
        "description": report["description"]
    }

@app.post("/report")
async def report(report: Report):
    try:
        report_data = report.dict()
        
        # Try MongoDB insertion and log the outcome
        try:
            result = reports_collection.insert_one(report_data)
            print(f"Inserted into MongoDB: {result.inserted_id}")
        except Exception as mongo_err:
            print(f"MongoDB insertion error: {mongo_err}")
            raise HTTPException(status_code=500, detail="Error inserting report into MongoDB")

        # Prepare data for Firebase and log the attempt
        firestore_data = {
            "url": report.url,
            "description": report.description,
            "timestamp": datetime.utcnow()
        }
        try:
            add_data("reports", str(result.inserted_id), firestore_data)
            print(f"Added to Firebase with ID: {result.inserted_id}")
        except Exception as firebase_err:
            print(f"Firebase insertion error: {firebase_err}")
            raise HTTPException(status_code=500, detail="Error inserting report into Firebase")

        # Find and return the newly inserted report
        inserted_report = reports_collection.find_one({"_id": result.inserted_id})
        if inserted_report:
            return {"message": "Report submitted successfully", "report": serialize_report(inserted_report)}
        else:
            raise HTTPException(status_code=404, detail="Report not found in MongoDB after insertion")

    except Exception as e:
        print(f"Error occurred: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@app.post("/scan")
async def scan(scan_request: ScanRequest):
    url = scan_request.url
    try:
        # Log the incoming URL for debugging
        print(f"Received URL for scanning: {url}")

        # Create a DataFrame for the input
        input_data = pd.DataFrame({
            "url": [url],
            "length_url": [len(url)],
            "length_hostname": [url.split('/')[2].count('.') if '://' in url else url.count('.')],
            "ip": [0],  # Placeholder for actual IP check
            "nb_dots": [url.count('.')],
            "nb_hyphens": [url.count('-')],
            "nb_at": [url.count('@')],
            "nb_qm": [url.count('?')],
            "nb_and": [url.count('&')],
            "nb_or": [url.count('|')],
            "nb_eq": [url.count('=')],
            "nb_underscore": [url.count('_')],
            "nb_tilde": [url.count('~')],
            "nb_percent": [url.count('%')],
            "nb_slash": [url.count('/')],
            "nb_star": [url.count('*')],
            "nb_colon": [url.count(':')],
            "nb_comma": [url.count(',')],
            "nb_semicolumn": [url.count(';')],
            "nb_dollar": [url.count('$')],
            "nb_space": [url.count(' ')],
            "nb_www": [url.count('www')],
            "nb_com": [url.count('.com')],
            "nb_dslash": [url.count('//')],
            "http_in_path": [1 if 'http' in url else 0],
            "https_token": [1 if 'https' in url else 0],

            # Add placeholders for missing features
            "avg_words_raw": [0],  # Example placeholder
            "avg_word_path": [0],
            "web_traffic": [0],
            "ratio_nullHyperlinks": [0],
            "domain_registration_length": [0],
            "punycode": [0],
            "phish_hints": [0],
            "longest_words_raw": [0],
            "tld_in_subdomain": [0],
            "empty_title": [0],
            "page_rank": [0],
            "abnormal_subdomain": [0],
            "tld_in_path": [0],
            "domain_in_brand": [0],
            "brand_in_path": [0],
            "shortest_word_host": [0],
            "whois_registered_domain": [0],
            "random_domain": [0],
            "longest_word_path": [0],
            "ratio_intErrors": [0],
            "nb_subdomains": [0],
            "ratio_digits_host": [0],
            "statistical_report": [0],
            "ratio_extMedia": [0],
            "domain_age": [0],
            "shortest_words_raw": [0],
            "longest_word_host": [0],
            "nb_extCSS": [0],
            "brand_in_subdomain": [0],
            "port": [0],
            "ratio_intHyperlinks": [0],
            "shortening_service": [0],
            "links_in_tags": [0],
            "ratio_intRedirection": [0],
            "prefix_suffix": [0],
            "google_index": [0],
            "onmouseover": [0],
            "avg_word_host": [0],
            "ratio_extRedirection": [0],
            "safe_anchor": [0],
            "nb_redirection": [0],
            "dns_record": [0],
            "nb_external_redirection": [0],
            "ratio_digits_url": [0],
            "ratio_extErrors": [0],
            "length_words_raw": [0],
            "submit_email": [0],
            "nb_hyperlinks": [0],
            "iframe": [0],
            "popup_window": [0],
            "login_form": [0],
            "domain_with_copyright": [0],
            "external_favicon": [0],
            "shortest_word_path": [0],
            "ratio_intMedia": [0],
            "path_extension": [0],
            "domain_in_title": [0],
            "right_clic": [0],
            "char_repeat": [0],
            "ratio_extHyperlinks": [0],
            "sfh": [0],
            "suspecious_tld": [0],
        })

        # Log the input DataFrame for debugging
        print(f"Input DataFrame for model:\n{input_data}")

        # Prepare the input data for the model
        prediction = model_pipeline.predict(input_data)

        result = {
            "url": url,
            "prediction": int(prediction[0])  # Convert to int for easier handling on the frontend
        }

        return result
    except Exception as e:
        # Log the error for debugging
        print(f"Error occurred during prediction: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@app.post("/update-model")
async def update_model():
    return {"message": "Model update triggered (logic to be implemented)"}
