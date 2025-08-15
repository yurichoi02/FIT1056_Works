# Fragment2_3.py
# Receptionist functions and helpers

from MSMS import app_data

def read_int(prompt):
    while True:
        try:
            return int(input(prompt))
        except ValueError:
            print("Invalid input. Please enter an integer.")

def read_str(prompt):
    value = input(prompt).strip()
    return value

def check_in(student_id):
    for s in app_data["students"]:
        if s["id"] == student_id:
            print(f"Student {s['name']} checked in.")
            return
    print("Student not found.")

def print_student_card(student_id):
    for s in app_data["students"]:
        if s["id"] == student_id:
            print(f"\n--- Student Card ---\nID: {s['id']}\nName: {s['name']}\nInstrument: {s['instrument']}\n")
            return
    print("Student not found.")
