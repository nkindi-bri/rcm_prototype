# app.py (Revised)
from flask import Flask, render_template, jsonify, request
from dataclasses import asdict
import csv
import json
from pathlib import Path

# Import the core logic from your scripts
from generate_rcm_testdata import make_encounters
from parse_rcm_documents import process_encounter

# Initialize the Flask application
app = Flask(__name__)

def load_csv_data():
    """Load encounter data from CSV file."""
    csv_path = Path("data/patient_encounters.csv")
    if not csv_path.exists():
        # Generate data if it doesn't exist
        from generate_rcm_testdata import main as generate_data
        generate_data()
    
    encounters_csv = []
    with csv_path.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            encounters_csv.append(row)
    return encounters_csv

def get_encounter_json(encounter_id: str):
    """Get the original JSON data for a specific encounter."""
    csv_data = load_csv_data()
    for row in csv_data:
        if row["encounter_id"] == encounter_id:
            return json.loads(row["original_json"])
    return None

# Load the demo encounter data from CSV on startup
CSV_ENCOUNTERS = load_csv_data()
ENCOUNTERS_DICT = {row["encounter_id"]: json.loads(row["original_json"]) for row in CSV_ENCOUNTERS}

@app.route('/')
def index():
    """Serves the main HTML page."""
    return render_template('index.html')

@app.route('/api/encounters', methods=['GET'])
def get_encounters():
    """Provides a list of available encounters for the frontend dropdown."""
    encounter_summaries = [
        {
            "id": row["encounter_id"],
            "description": f"{row['encounter_id']}: {row['reason_for_visit']}"
        }
        for row in CSV_ENCOUNTERS
    ]
    return jsonify(encounter_summaries)

@app.route('/api/encounters_csv', methods=['GET'])
def get_encounters_csv():
    """Provides the CSV encounter data as JSON for table display."""
    # Return CSV data without the original_json column for cleaner display
    clean_data = []
    for row in CSV_ENCOUNTERS:
        clean_row = {k: v for k, v in row.items() if k != "original_json"}
        clean_data.append(clean_row)
    return jsonify(clean_data)

@app.route('/api/encounters_full', methods=['GET'])
def get_encounters_full():
    """Provides the full JSON data for all encounters."""
    return jsonify(ENCOUNTERS_DICT)

@app.route('/api/process', methods=['POST'])
def process_api():
    """The core API endpoint for processing a single encounter."""
    if not request.json:
        return jsonify({"error": "Invalid request: missing JSON body"}), 400

    encounter_data = request.json

    try:
        results = process_encounter(encounter_data)
        return jsonify(results)
    except Exception as e:
        # It's good practice to log the error on the server
        print(f"Error processing encounter: {e}")
        return jsonify({"error": f"An error occurred during processing: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True, port=8080)
