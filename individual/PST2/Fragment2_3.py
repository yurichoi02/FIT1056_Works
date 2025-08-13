# --- New Receptionist Features ---

def check_in(student_id, course_id, timestamp=None):
    """Record student attendance."""
    if timestamp is None:
        timestamp = datetime.datetime.now().isoformat()

    record = {"student_id": student_id, "course_id": course_id, "timestamp": timestamp}
    app_data["attendance"].append(record)
    print(f"Student {student_id} checked into {course_id}.")


def print_student_card(student_id):
    """Create a student ID badge text file."""
    student = None
    for s in app_data["students"]:
        if s["id"] == student_id:
            student = s
            break

    if student:
        filename = f"{student_id}_card.txt"
        with open(filename, "w") as f:
            f.write("========================\n")
            f.write("  MUSIC SCHOOL ID BADGE\n")
            f.write("========================\n")
            f.write(f"ID: {student['id']}\n")
            f.write(f"Name: {student['name']}\n")
            enrolled = ", ".join(student.get("enrolled_in", []))
            f.write(f"Enrolled In: {enrolled}\n")
        print(f"Card saved to {filename}.")
    else:
        print(f"No student found with ID {student_id}.")


# --- Input Helpers ---
def read_int(prompt):
    """Get an integer from user input."""
    while True:
        val = input(prompt).strip()
        if val.isdigit():
            return int(val)
        else:
            print("Please enter a valid number.")


def read_str(prompt, allow_empty=False):
    """Get a string from user input."""
    while True:
        s = input(prompt).strip()
        if s or allow_empty:
            return s
        print("Please enter something.")
