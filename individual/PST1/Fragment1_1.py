# MSMS.py - The In-Memory Prototype

# --- Data Models ---
class Student:
    """A blueprint for student objects. Holds their info."""
    def __init__(self, student_id, name):
        self.id = student_id
        self.name = name
        self.enrolled_in = []  # DONE

class Teacher:
    """A blueprint for teacher objects."""
    def __init__(self, teacher_id, name, speciality):
        self.id = teacher_id      # DONE
        self.name = name
        self.speciality = speciality

# --- In-Memory Databases ---
student_db = []         # DONE
teacher_db = []
next_student_id = 1
next_teacher_id = 1
