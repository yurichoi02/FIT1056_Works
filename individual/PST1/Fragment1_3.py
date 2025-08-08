# --- Front Desk Functions ---
# These are the "receptionist tools" — the kind of actions someone at the front desk
# of the music school might do: register students, enrol them, and look up records.

def find_student_by_id(student_id):
    # This looks through our student list to find a specific student by their ID.
    # If it finds them, it gives back (returns) that student.
    # If not, it returns "None" (meaning: we didn’t find anything).
    for student in student_db:
        if student.id == student_id:
            return student
    return None

def front_desk_register(name, instrument):
    # This is for signing up a brand-new student.
    global next_student_id  # So we can use and update the next available ID number.
    new_student = Student(next_student_id, name)  # Make a new Student object.
    student_db.append(new_student)  # Store this student in our list.
    next_student_id += 1  # Move to the next ID number for the next student.
    # Enrol the new student in their chosen instrument class.
    front_desk_enrol(new_student.id, instrument)
    print(f"Front Desk: Successfully registered '{name}' and enrolled them in '{instrument}'.")

def front_desk_enrol(student_id, instrument):
    # This signs up an existing student for an instrument class.
    student = find_student_by_id(student_id)  # First, find them by their ID.
    if student:
        student.enrolled_in.append(instrument)  # Add the instrument to their list.
        print(f"Front Desk: Enrolled student {student_id} in '{instrument}'.")
    else:
        print(f"Error: Student ID {student_id} not found.")  # If we can’t find them.

def front_desk_lookup(term):
    # This searches BOTH students and teachers for a given keyword.
    print(f"\n--- Performing lookup for '{term}' ---")
    find_students(term)   # Search the student list.
    find_teachers(term)   # Search the teacher list.
