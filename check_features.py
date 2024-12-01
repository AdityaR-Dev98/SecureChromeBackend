from app.utils.utils import extract_url_features

url = "https://www.google.com/"
features = extract_url_features(url)

# Print all features and their values
print("Extracted Features:")
for key, value in features.items():
    print(f"{key}: {value}")

# Ensure features match the expected input format of the model
try:
    feature_values = [float(features[key]) for key in expected_feature_order]
    print("Features successfully converted to float.")
except Exception as e:
    print("Error during feature conversion:", str(e))
