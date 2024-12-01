import validators  # To validate the URL
from fastapi import APIRouter, HTTPException
import joblib
import pandas as pd
from app.utils.utils import extract_url_features

MODEL_PATH="C:\\Users\\rasto\\Downloads\\SecureChromeBackend\\random_forest_pipeline.pkl"
# Load the trained model pipeline
try:
    model_pipeline = joblib.load(MODEL_PATH)
except Exception as e:
    raise RuntimeError(f"Error loading model: {str(e)}")

# Router instance
router = APIRouter()

@router.post("/scan")
async def scan(url: str):
    try:
        # Validate the URL
        if not url or not validators.url(url):
            raise HTTPException(status_code=400, detail="Invalid URL provided.")

        # Extract features using the utility function
        features = extract_url_features(url)

        # Convert features into a DataFrame for prediction
        input_data = pd.DataFrame([features])

        # Get expected features from the model pipeline
        expected_features = model_pipeline.feature_names_in_ if hasattr(model_pipeline, "feature_names_in_") else input_data.columns

        # Ensure all expected features are present, adding missing ones with default value 0
        for feature in expected_features:
            if feature not in input_data.columns:
                input_data[feature] = 0

        # Drop any extra columns not expected by the model
        input_data = input_data[expected_features]

        # Convert numeric columns to floats and non-numeric columns to strings
        for column in input_data.columns:
            if input_data[column].dtype == "object":
                input_data[column] = input_data[column].astype(str).fillna("")
            else:
                input_data[column] = pd.to_numeric(input_data[column], errors="coerce").fillna(0)

        # Predict with the model pipeline
        prediction = model_pipeline.predict(input_data)

        return {"url": url, "prediction": int(prediction[0])}

    except HTTPException as e:
        raise e
    except Exception as e:
        return {"url": url, "prediction": f"Error: {str(e)}"}
