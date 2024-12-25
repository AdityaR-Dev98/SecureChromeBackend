import joblib
import pandas as pd
from pymongo import MongoClient
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from app.utils.utils import extract_url_features  # Import the feature extraction function
import validators  # To validate the URL
import logging

# MongoDB setup
client = MongoClient("mongodb://localhost:27017/")
db = client["secure_chrome_extension"]

# Load the current model
MODEL_PATH = "-"
try:
    model_pipeline = joblib.load(MODEL_PATH)
except FileNotFoundError:
    raise Exception(f"Model not found at {MODEL_PATH}. Please provide a valid path.")

async def update_prediction_based_on_reports(url: str):
    """Update model prediction based on user reports."""
    if not validators.url(url):
        logging.warning(f"Invalid URL provided: {url}. Skipping update.")
        return  # Skip this URL or handle with default values

    reports = list(db["reports"].find({"url": url}))

    if not reports:
        logging.info(f"No relevant reports found for the URL: {url}.")
        return

    # Extract features for the URL
    try:
        feature_data = pd.DataFrame([extract_url_features(url)])
    except Exception as e:
        logging.error(f"Feature extraction failed for URL {url}: {str(e)}")
        return

    # Handle missing features
    feature_data = feature_data.fillna(0)  # Fill missing features with default values

    # Create labels (1 for malicious, 0 for safe)
    labels = [
        1 if "malicious" in report.get("description", "").lower() else 0
        for report in reports
    ]

    # Retrain the model with updated data
    new_model = retrain_model(feature_data, labels)

    # Save the updated model
    try:
        joblib.dump(new_model, MODEL_PATH)
        logging.info(f"Model successfully updated and saved to {MODEL_PATH}.")
    except Exception as e:
        logging.error(f"Failed to save the updated model: {str(e)}")

def retrain_model(features, labels):
    """Retrain the RandomForest model with new data."""
    pipeline = Pipeline([
        ("scaler", StandardScaler()),
        ("classifier", RandomForestClassifier(n_estimators=100, random_state=42))
    ])
    pipeline.fit(features, labels)
    return pipeline
