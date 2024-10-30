from fastapi import FastAPI, HTTPException
import joblib
import numpy as np  # Import numpy for array reshaping
import pandas as pd  # Import pandas for DataFrame creation

# Load the trained model pipeline (includes preprocessor and classifier)
model_pipeline = joblib.load('C:\\Users\\rasto\\Downloads\\SecureChromeBackend\\random_forest_pipeline.pkl')

# Initialize FastAPI app
app = FastAPI()

@app.post("/scan")
async def scan(url: str):
    try:
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
            # Add additional features expected by your model
            **{feature: [0] for feature in model_pipeline.named_steps['preprocessor'].transformers_[1][1].get_feature_names_out() if feature not in ['url']}
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
    except ValueError as ve:
        # Specific error handling for value errors
        print(f"ValueError occurred: {str(ve)}")
        raise HTTPException(status_code=400, detail="Invalid input data")
    except Exception as e:
        # Log the error for debugging
        print(f"Error occurred during prediction: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")