# --- Core Helper Functions ---
# These are the main little jobs (functions) our system can do right now.

def add_teacher(name, speciality):
    # We say "global" here so we can change the value of next_teacher_id that’s outside this function
    global next_teacher_id

    # Make a new Teacher object using the current ID, name, and speciality
    new_teacher = Teacher(next_teacher_id, name, speciality)

    # Put this new teacher into our teacher_db list
    teacher_db.append(new_teacher)

    # Increase the ID number so the next teacher gets a new unique ID
    next_teacher_id += 1

    # Just to tell the user it worked
    print(f"Core: Teacher '{name}' added successfully.")

def list_students():
    # Show a nice header
    print("\n--- Student List ---")

    # If we don’t have any students yet, say so and stop
    if not student_db:
        print("No students in the system.")
        return

    # Go through every student in the list and print their details
    for student in student_db:
        print(f"  ID: {student.id}, Name: {student.name}, Enrolled in: {student.enrolled_in}")

def list_teachers():
    # Show a nice header
    print("\n--- Teacher List ---")

    # Go through every teacher in the list and print their details
    for teacher in teacher_db:
        print(f"  ID: {teacher.id}, Name: {teacher.name}, Speciality: {teacher.speciality}")

def find_students(term):
    # Tell the user what we’re searching for
    print(f"\n--- Finding Students matching '{term}' ---")

    # Look for students whose name contains the search term (ignoring upper/lowercase)
    results = [s for s in student_db if term.lower() in s.name.lower()]

    # If no students match, say so
    if not results:
        print("No match found.")
    else:
        # Show each matching student
        for student in results:
            print(f"  ID: {student.id}, Name: {student.name}, Enrolled in: {student.enrolled_in}")

def find_teachers(term):
    # Tell the user what we’re searching for
    print(f"\n--- Finding Teachers matching '{term}' ---")

    # Look for teachers whose name or speciality contains the search term
    results = [
        t for t in teacher_db
        if term.lower() in t.name.lower() or term.lower() in t.speciality.lower()
    ]

    # If no teachers match, say so
    if not results:
        print("No match found.")
    else:
        # Show each matching teacher
        for teacher in results:
            print(f"  ID: {teacher.id}, Name: {teacher.name}, Speciality: {teacher.speciality}")
