# MSMS.py - Music School Management System (Prototype)
# This is my attempt at making a simple in-memory system
# to store students, teachers, and classes for our project.
# Everything is stored in variables, not a database (yet).

# -------------------------------
# Data Models
# -------------------------------

class Student:
    """Represents a student in the music school."""
    def __init__(self, student_id, name):
        # Store ID and name for each student
        self.id = student_id
        self.name = name
        # Keep track of what classes the student is in
        self.enrolled_in = []

class Teacher:
    """Represents a teacher in the music school."""
    def __init__(self, teacher_id, name, speciality):
        # Store teacher's ID, name, and what instrument/subject they teach
        self.id = teacher_id
        self.name = name
        self.speciality = speciality

class Course:
    """Represents a music course or class."""
    def __init__(self, course_id, title, teacher):
        # Every course has an ID, title, and assigned teacher
        self.id = course_id
        self.title = title
        self.teacher = teacher
        # Keep track of students in this course
        self.students = []

# -------------------------------
# "Database" (in memory)
# -------------------------------
students = {}  # Stores all students by their ID
teachers = {}  # Stores all teachers by their ID
courses = {}   # Stores all courses by their ID

# -------------------------------
# Functions for adding things
# -------------------------------

def add_student(student_id, name):
    """Adds a new student to the system."""
    if student_id in students:
        print("Student already exists!")
    else:
        students[student_id] = Student(student_id, name)
        print(f"Student '{name}' added successfully!")

def add_teacher(teacher_id, name, speciality):
    """Adds a new teacher to the system."""
    if teacher_id in teachers:
        print("Teacher already exists!")
    else:
        teachers[teacher_id] = Teacher(teacher_id, name, speciality)
        print(f"Teacher '{name}' added successfully!")

def add_course(course_id, title, teacher_id):
    """Adds a new course to the system and assigns a teacher."""
    if course_id in courses:
        print("Course already exists!")
    elif teacher_id not in teachers:
        print("Teacher not found!")
    else:
        teacher = teachers[teacher_id]
        courses[course_id] = Course(course_id, title, teacher)
        print(f"Course '{title}' added successfully!")

# -------------------------------
# Enrolling students into courses
# -------------------------------

def enroll_student(student_id, course_id):
    """Enrolls an existing student into an existing course."""
    if student_id not in students:
        print("Student not found!")
    elif course_id not in courses:
        print("Course not found!")
    else:
        student = students[student_id]
        course = courses[course_id]
        # Add student to course and course to student
        student.enrolled_in.append(course)
        course.students.append(student)
        print(f"Student '{student.name}' enrolled in '{course.title}'!")

# -------------------------------
# Display functions
# -------------------------------

def list_students():
    """Shows all students and their enrolled courses."""
    if not students:
        print("No students found!")
    else:
        for s in students.values():
            course_titles = [c.title for c in s.enrolled_in]
            print(f"{s.id} - {s.name} | Courses: {', '.join(course_titles) or 'None'}")

def list_teachers():
    """Shows all teachers and what they teach."""
    if not teachers:
        print("No teachers found!")
    else:
        for t in teachers.values():
            print(f"{t.id} - {t.name} | Speciality: {t.speciality}")

def list_courses():
    """Shows all courses and who is teaching them."""
    if not courses:
        print("No courses found!")
    else:
        for c in courses.values():
            print(f"{c.id} - {c.title} | Teacher: {c.teacher.name}")

# -------------------------------
# Test Data (just for now)
# -------------------------------
# These are sample entries to test if things work.
# Later, we can remove or replace them.

if __name__ == "__main__":
    add_teacher("T1", "Alice", "Piano")
    add_teacher("T2", "Bob", "Guitar")
    add_student("S1", "Charlie")
    add_student("S2", "Daisy")
    add_course("C1", "Beginner Piano", "T1")
    add_course("C2", "Intermediate Guitar", "T2")
    enroll_student("S1", "C1")
    enroll_student("S2", "C2")
    print("\n--- Students ---")
    list_students()
    print("\n--- Teachers ---")
    list_teachers()
    print("\n--- Courses ---")
    list_courses()
