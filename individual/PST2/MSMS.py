# pst2_main.py - The Persistent Application

import json
import datetime

DATA_FILE = "msms.json"
app_data = {}  # Holds all data for the application

# --- Core Persistence Engine ---
def load_data(path=DATA_FILE):
    """Load data from a JSON file, or start fresh if file not found."""
    global app_data
    try:
        with open(path, "r") as f:
            app_data = json.load(f)
            print("Data loaded.")
    except FileNotFoundError:
        print("No data file found. Starting with empty data.")
        app_data = {
            "students": [],
            "teachers": [],
            "attendance": [],
            "next_student_id": 1,
            "next_teacher_id": 1
        }


def save_data(path=DATA_FILE):
    """Save all data to a JSON file."""
    with open(path, "w") as f:
        json.dump(app_data, f, indent=4)
    print("Data saved.")