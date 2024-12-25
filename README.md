<H1>SecureChromeExtension</H1>

SecureChromeExtension is a lightweight Chrome extension designed to detect phishing and malicious websites in real-time. By leveraging machine learning and crowdsourced user reports, it enhances web security by providing users with immediate feedback on the safety of the websites they visit.

If a website is detected as malicious, users are alerted instantly, and they can report incorrect classifications to improve accuracy over time.

<H2>Features</H2>

Real-time Website Scanning: Automatically scans the currently opened webpage and predicts if it is safe or malicious.

Machine Learning Model: Utilizes a Random Forest model for URL classification based on URL structure, length, and special character patterns.

Crowdsourced Reporting: Users can report URLs as either safe or malicious. If a URL is reported 10 times, the model's prediction adapts accordingly.

PhishTank API Integration: Checks URLs against the PhishTank database for known phishing sites.

Firebase Storage: Records scan results and user reports in Firestore for persistent storage.

User-Friendly Interface: Minimalist popup UI for easy scanning and reporting.

Notification System: Alerts users with Chrome notifications when malicious sites are detected.

<h2>Tech Stack<h2>

Frontend: HTML, CSS, JavaScript (Chrome Extension)

Backend: FastAPI (Python)

Database: MongoDB (for URL reports and scans)

Cloud Storage: Firebase Firestore

Machine Learning: Random Forest Classifier with Label Encoder

API: PhishTank API Integration

<h2>How It Works</h2>

Scan: When the user clicks "Scan", the extension captures the active tab URL and sends it to the FastAPI backend.

Prediction: The backend uses the machine learning model to predict if the URL is malicious.

Override by Reports: If the URL has been reported more than 10 times as either safe or malicious, the system overrides the model prediction.

Report: Users can submit incorrect results to improve detection accuracy.

Storage: Reports and scan logs are stored in MongoDB and Firebase Firestore.

<h2>Installation</h2>

Clone this repository.

Open Chrome and navigate to chrome://extensions/.

Enable "Developer Mode" in the top-right corner.

Click "Load Unpacked" and select the cloned repository's folder.

The extension will now appear in your extensions list.

<h2>Configuration</h2>

Backend Setup:

Clone the SecureChromeBackend repository.

Install dependencies: pip install -r requirements.txt

Run the FastAPI server: uvicorn app.main:app --reload

Firebase:

Create a Firebase project.

Set up Firestore in Native mode.

Replace Firebase credentials in the backend.

<h2>Project Structure</h2>

SecureChromeExtension/

├── manifest.json          # Chrome extension manifest

├── popup.html             # Popup interface for scanning/reporting

├── popup.js               # JS logic for scanning and reporting

├── styles.css             # Popup styling

SecureChromeBackend/

├── app/

│   ├── main.py            # FastAPI main application

│   ├── routers/

│   │   ├── scan.py        # Scan endpoint

│   │   ├── report.py      # Report endpoint

│   │   └── update_model.py # Model update endpoint

│   └── models/            # Database models

└── requirements.txt       # Python dependencies

