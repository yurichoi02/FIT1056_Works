# MSMS.py - The In-Memory Prototype

# --- Data Models ---
class Student:
    def __init__(self, student_id, name):
        self.id = student_id
        self.name = name
        self.enrolled_in = []


class Teacher:
    def __init__(self, teacher_id, name, speciality):
        self.id = teacher_id
        self.name = name
        self.speciality = speciality


# --- In-Memory Data Stores ---
student_db = []
teacher_db = []
next_student_id = 1
next_teacher_id = 1

# --- Core Helper Functions ---


def add_teacher(name, speciality):
    global next_teacher_id
    if not name.strip() or not speciality.strip():
        print("Name and speciality cannot be empty.")
        return
    new_teacher = Teacher(next_teacher_id, name.strip(), speciality.strip())
    teacher_db.append(new_teacher)
    next_teacher_id += 1
    print(
        f"Teacher '{new_teacher.name}' added (speciality: {new_teacher.speciality}).")


def list_students():
    print("\n--- Students ---")
    if not student_db:
        print("(none)")
        return
    for s in student_db:
        instruments = ", ".join(
            s.enrolled_in) if s.enrolled_in else "(no instruments)"
        print(f"[{s.id}] {s.name} → {instruments}")


def list_teachers():
    print("\n--- Teachers ---")
    if not teacher_db:
        print("(none)")
        return
    for t in teacher_db:
        print(f"[{t.id}] {t.name} (speciality: {t.speciality})")


def find_students(term):
    term = term.strip().lower()
    print(f"\nSearch students: '{term}'")
    results = [s for s in student_db if term in s.name.lower()]
    if not results:
        print("(no matches)")
        return
    for s in results:
        instruments = ", ".join(
            s.enrolled_in) if s.enrolled_in else "(no instruments)"
        print(f"- [{s.id}] {s.name} → {instruments}")


def find_teachers(term):
    term = term.strip().lower()
    print(f"\nSearch teachers: '{term}'")
    results = [t for t in teacher_db if term in t.name.lower()
               or term in t.speciality.lower()]
    if not results:
        print("(no matches)")
        return
    for t in results:
        print(f"- [{t.id}] {t.name} (speciality: {t.speciality})")

# --- Front Desk Functions ---


def find_student_by_id(student_id):
    for s in student_db:
        if s.id == student_id:
            return s
    return None


def front_desk_register(name, instrument):
    global next_student_id
    name = name.strip()
    instr = instrument.strip()
    if not name:
        print("Name cannot be empty.")
        return
    new_student = Student(next_student_id, name)
    next_student_id += 1
    if instr:
        new_student.enrolled_in.append(instr)
    student_db.append(new_student)
    print(f"Student '{new_student.name}' registered with ID {new_student.id}.")
    if instr:
        print(f"Enrolled in '{instr}'.")


def front_desk_enrol(student_id, instrument):
    student = find_student_by_id(student_id)
    if not student:
        print(f"No student with ID {student_id}.")
        return
    instr = instrument.strip()
    if not instr:
        print("Instrument cannot be empty.")
        return
    if instr in student.enrolled_in:
        print(f"{student.name} already enrolled in '{instr}'.")
        return
    student.enrolled_in.append(instr)
    print(f"{student.name} enrolled in '{instr}'.")


def front_desk_lookup(term):
    find_students(term)
    find_teachers(term)

# --- Extra A: Instrument Insights ---


def list_instruments_summary():
    counts = {}
    for s in student_db:
        for instr in s.enrolled_in:
            key = instr.strip().lower()
            counts[key] = counts.get(key, 0) + 1
    print("\n--- Instrument Summary ---")
    if not counts:
        print("(none)")
        return
    for instr in sorted(counts.keys()):
        print(f"{instr.title()} - {counts[instr]} student(s)")


def find_students_by_instrument(term):
    term = term.strip().lower()
    print(f"\nStudents learning '{term}':")
    results = []
    for s in student_db:
        if any(term in instr.lower() for instr in s.enrolled_in):
            results.append(s)
    if not results:
        print("(no matches)")
        return
    for s in results:
        instruments = ", ".join(
            s.enrolled_in) if s.enrolled_in else "(no instruments)"
        print(f"- [{s.id}] {s.name} → {instruments}")


# --- Extra B: Teacher Assignments ---
# (student_id, instrument_lower) -> teacher_id
lesson_assignments = {}


def find_teacher_by_id(teacher_id):
    for t in teacher_db:
        if t.id == teacher_id:
            return t
    return None


def assign_teacher(student_id, instrument, teacher_id):
    student = find_student_by_id(student_id)
    if not student:
        print(f"No student with ID {student_id}.")
        return
    teacher = find_teacher_by_id(teacher_id)
    if not teacher:
        print(f"No teacher with ID {teacher_id}.")
        return
    instr = instrument.strip()
    if instr not in student.enrolled_in:
        print(f"{student.name} not enrolled in '{instr}'.")
        return
    if teacher.speciality.strip().lower() != instr.lower():
        print(
            f"Teacher '{teacher.name}' speciality is '{teacher.speciality}', not '{instr}'.")
        return
    key = (student.id, instr.lower())
    lesson_assignments[key] = teacher.id
    print(f"Assigned {teacher.name} → {student.name} for {instr}.")


def view_assignments_for_student(student_id):
    student = find_student_by_id(student_id)
    if not student:
        print(f"No student with ID {student_id}.")
        return
    print(f"\nAssignments for {student.name}:")
    if not student.enrolled_in:
        print("(no instruments)")
        return
    for instr in student.enrolled_in:
        key = (student.id, instr.lower())
        if key in lesson_assignments:
            t = find_teacher_by_id(lesson_assignments[key])
            if t:
                print(f"{instr}: {t.name} (ID {t.id})")
            else:
                print(f"{instr}: (teacher not found)")
        else:
            print(f"{instr}: (no teacher assigned)")

# --- Main Menu ---


def main():
    while True:
        print("\n=== MSMS Menu ===")
        print("1. Register new student (and enrol in an instrument)")
        print("2. Enrol existing student in another instrument")
        print("3. Add teacher")
        print("4. List students")
        print("5. List teachers")
        print("6. Lookup (students & teachers)")
        print("7. Instrument summary")
        print("8. Find students by instrument")
        print("9. Assign teacher to student (by instrument)")
        print("10. View a student's teacher assignments")
        print("0. Exit")
        choice = input("Select option: ").strip()

        if choice == "1":
            name = input("Student name: ").strip()
            instrument = input("Instrument: ").strip()
            front_desk_register(name, instrument)

        elif choice == "2":
            try:
                sid = int(input("Student ID: "))
            except ValueError:
                print("Invalid ID.")
                continue
            instr = input("Instrument: ").strip()
            front_desk_enrol(sid, instr)

        elif choice == "3":
            name = input("Teacher name: ").strip()
            speciality = input("Speciality: ").strip()
            add_teacher(name, speciality)

        elif choice == "4":
            list_students()

        elif choice == "5":
            list_teachers()

        elif choice == "6":
            term = input("Search term: ").strip()
            if term:
                front_desk_lookup(term)
            else:
                print("Search term cannot be empty.")

        elif choice == "7":
            list_instruments_summary()

        elif choice == "8":
            term = input("Instrument search: ").strip()
            if term:
                find_students_by_instrument(term)
            else:
                print("Instrument search cannot be empty.")

        elif choice == "9":
            try:
                sid = int(input("Student ID: "))
                instr = input("Instrument: ").strip()
                tid = int(input("Teacher ID: "))
            except ValueError:
                print("Invalid ID.")
                continue
            assign_teacher(sid, instr, tid)

        elif choice == "10":
            try:
                sid = int(input("Student ID: "))
            except ValueError:
                print("Invalid ID.")
                continue
            view_assignments_for_student(sid)

        elif choice == "0":
            break

        else:
            print("Invalid option.")


if __name__ == "__main__":
    main()
