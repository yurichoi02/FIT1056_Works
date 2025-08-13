# --- Full CRUD for Core Data ---
# Note: We are now working with lists of dictionaries, not lists of objects.

def add_teacher(name, speciality):
    """Add a new teacher."""
    teacher_id = app_data["next_teacher_id"]
    new_teacher = {"id": teacher_id, "name": name, "speciality": speciality}
    app_data["teachers"].append(new_teacher)
    app_data["next_teacher_id"] += 1
    print(f"Teacher '{name}' added with ID {teacher_id}.")


def update_teacher(teacher_id, **fields):
    """Update teacher details."""
    for teacher in app_data["teachers"]:
        if teacher["id"] == teacher_id:
            for key, value in fields.items():
                if value:  # Only update if not empty
                    teacher[key] = value
            print(f"Teacher {teacher_id} updated.")
            return
    print(f"No teacher found with ID {teacher_id}.")


def remove_teacher(teacher_id):
    """Remove a teacher by ID."""
    before = len(app_data["teachers"])
    app_data["teachers"] = [t for t in app_data["teachers"] if t["id"] != teacher_id]
    if len(app_data["teachers"]) < before:
        print(f"Teacher {teacher_id} removed.")
    else:
        print(f"No teacher found with ID {teacher_id}.")


def update_student(student_id, **fields):
    """Update student details."""
    for student in app_data["students"]:
        if student["id"] == student_id:
            for key, value in fields.items():
                if value:
                    student[key] = value
            print(f"Student {student_id} updated.")
            return
    print(f"No student found with ID {student_id}.")


def remove_student(student_id):
    """Remove a student by ID."""
    before = len(app_data["students"])
    app_data["students"] = [s for s in app_data["students"] if s["id"] != student_id]
    if len(app_data["students"]) < before:
        print(f"Student {student_id} removed.")
    else:
        print(f"No student found with ID {student_id}.")