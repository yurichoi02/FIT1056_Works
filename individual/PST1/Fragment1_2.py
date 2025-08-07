# --- Core Helper Functions ---
def add_teacher(name, speciality):
    global next_teacher_id
    new_teacher = Teacher(next_teacher_id, name, speciality)
    teacher_db.append(new_teacher)
    next_teacher_id += 1
    print(f"Core: Teacher '{name}' added successfully.")

def list_students():
    print("\n--- Student List ---")
    if not student_db:
        print("No students in the system.")
        return
    for student in student_db:
        print(f"  ID: {student.id}, Name: {student.name}, Enrolled in: {student.enrolled_in}")

def list_teachers():
    print("\n--- Teacher List ---")
    for teacher in teacher_db:
        print(f"  ID: {teacher.id}, Name: {teacher.name}, Speciality: {teacher.speciality}")

def find_students(term):
    print(f"\n--- Finding Students matching '{term}' ---")
    results = [s for s in student_db if term.lower() in s.name.lower()]
    if not results:
        print("No match found.")
    else:
        for student in results:
            print(f"  ID: {student.id}, Name: {student.name}, Enrolled in: {student.enrolled_in}")

def find_teachers(term):
    print(f"\n--- Finding Teachers matching '{term}' ---")
    results = [
        t for t in teacher_db
        if term.lower() in t.name.lower() or term.lower() in t.speciality.lower()
    ]
    if not results:
        print("No match found.")
    else:
        for teacher in results:
            print(f"  ID: {teacher.id}, Name: {teacher.name}, Speciality: {teacher.speciality}")
