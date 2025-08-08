# MSMS.py - The In-Memory Prototype
# This file is like a "practice" version of our music school system.
# Right now, we’re just keeping all the info in memory (RAM), not in a real database.

# --- Data Models (aka blueprints for objects) ---

class Student:
    """This is a plan for making Student objects. Each student has an ID, name, and courses they’re in."""
    def __init__(self, student_id, name):
        # Store the student's ID (like their unique number)
        self.id = student_id
        # Store their name
        self.name = name
        # This will be a list of course IDs that the student is enrolled in
        self.enrolled_in = []  # starts empty because they haven’t joined any course yet

class Teacher:
    """This is a plan for making Teacher objects. Each teacher has an ID, name, and a speciality."""
    def __init__(self, teacher_id, name, speciality):
        # Store the teacher's ID
        self.id = teacher_id
        # Store their name
        self.name = name
        # Store what they’re best at teaching
        self.speciality = speciality

# --- In-Memory Databases (just lists for now) ---
# These lists will keep all the students and teachers we add
student_db = []    # will hold Student objects
teacher_db = []    # will hold Teacher objects

# These variables help us keep track of the next unique ID to give out
next_student_id = 1
next_teacher_id = 1
