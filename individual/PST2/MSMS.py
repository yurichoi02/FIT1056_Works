# MSMS.py
# Core data store for the Music School Management System (MSMS)

# Global app data dictionary
app_data = {
    "teachers": [],
    "students": [],
    "next_teacher_id": 1,
    "next_student_id": 1
}

def load_data():
    """Loads initial data into the system (in-memory only for PST2)."""
    app_data["teachers"] = [
        {"id": 1, "name": "John Smith", "speciality": "Piano"}
    ]
    app_data["students"] = [
        {"id": 1, "name": "Alice Tan", "instrument": "Piano"}
    ]
    app_data["next_teacher_id"] = 2
    app_data["next_student_id"] = 2

def save_data():
    """Pretends to save data (no file handling in PST2)."""
    print("\n[Data saved successfully]")
