# --- Front Desk Functions ---
def find_student_by_id(student_id):
    for student in student_db:
        if student.id == student_id:
            return student
    return None

def front_desk_register(name, instrument):
    global next_student_id
    new_student = Student(next_student_id, name)
    student_db.append(new_student)
    next_student_id += 1
    front_desk_enrol(new_student.id, instrument)
    print(f"Front Desk: Successfully registered '{name}' and enrolled them in '{instrument}'.")

def front_desk_enrol(student_id, instrument):
    student = find_student_by_id(student_id)
    if student:
        student.enrolled_in.append(instrument)
        print(f"Front Desk: Enrolled student {student_id} in '{instrument}'.")
    else:
        print(f"Error: Student ID {student_id} not found.")

def front_desk_lookup(term):
    print(f"\n--- Performing lookup for '{term}' ---")
    find_students(term)
    find_teachers(term)
