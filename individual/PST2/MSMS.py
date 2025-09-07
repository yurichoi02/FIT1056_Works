# MSMS.py – PST2
# JSON persistence, CRUD, receptionist features, and CSV export
import json
import os
import datetime
import csv

DATA_FILE = "msms.json"

# -------------------
# App state
# -------------------
app_data = {
    "students": [],
    "teachers": [],
    "attendance": [],
    "next_student_id": 1,
    "next_teacher_id": 1,
    # list of {"student_id", "instrument", "teacher_id"}
    "lesson_assignments": []
}

# -------------------
# Persistence
# -------------------


def load_data(path=DATA_FILE):
    global app_data
    if not os.path.exists(path):
        print(f"(no {path}, starting fresh)")
        return
    with open(path, "r", encoding="utf-8") as f:
        app_data = json.load(f)
    # normalize
    for s in app_data.get("students", []):
        s["instruments"] = [norm(i) for i in s.get("instruments", [])]
    for t in app_data.get("teachers", []):
        t["speciality"] = norm(t.get("speciality", ""))
    print(f"Loaded from {path}")


def save_data(path=DATA_FILE):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(app_data, f, indent=2)
    print(f"Saved to {path}")


def autosave():
    try:
        save_data()
    except Exception as e:
        print(f"(autosave failed: {e})")

# -------------------
# Helpers
# -------------------


def norm(instr: str) -> str:
    return (instr or "").strip().title()


def nonempty(s: str) -> bool:
    return bool(s and s.strip())


def find_student_by_id(sid: int):
    for s in app_data["students"]:
        if s["id"] == sid:
            return s
    return None


def find_teacher_by_id(tid: int):
    for t in app_data["teachers"]:
        if t["id"] == tid:
            return t
    return None

# -------------------
# Student CRUD
# -------------------


def add_student(name, first_instrument=""):
    if not nonempty(name):
        print("Name cannot be empty.")
        return
    s = {
        "id": app_data["next_student_id"],
        "name": name.strip(),
        "instruments": []
    }
    app_data["next_student_id"] += 1
    fi = norm(first_instrument)
    if nonempty(fi):
        s["instruments"].append(fi)
    app_data["students"].append(s)
    print(f"Student '{s['name']}' added with ID {s['id']}.")
    if nonempty(fi):
        print(f"Enrolled in '{fi}'.")
    autosave()


def update_student(sid, new_name=None):
    s = find_student_by_id(sid)
    if not s:
        print(f"No student with ID {sid}.")
        return
    if nonempty(new_name):
        s["name"] = new_name.strip()
    print(f"Student [{sid}] updated.")
    autosave()


def remove_student(sid):
    s = find_student_by_id(sid)
    if not s:
        print(f"No student with ID {sid}.")
        return
    # clean up
    app_data["lesson_assignments"] = [
        a for a in app_data["lesson_assignments"] if a["student_id"] != sid]
    app_data["attendance"] = [
        a for a in app_data["attendance"] if a["student_id"] != sid]
    app_data["students"] = [x for x in app_data["students"] if x["id"] != sid]
    print(f"Student [{sid}] removed.")
    autosave()


def enrol_instrument(sid, instrument):
    s = find_student_by_id(sid)
    if not s:
        print(f"No student with ID {sid}.")
        return
    instr = norm(instrument)
    if not nonempty(instr):
        print("Instrument cannot be empty.")
        return
    if instr in s["instruments"]:
        print(f"{s['name']} already enrolled in '{instr}'.")
        return
    s["instruments"].append(instr)
    print(f"{s['name']} enrolled in '{instr}'.")
    autosave()

# -------------------
# Teacher CRUD
# -------------------


def add_teacher(name, speciality):
    if not (nonempty(name) and nonempty(speciality)):
        print("Name and speciality cannot be empty.")
        return
    name = name.strip()
    spec = norm(speciality)
    for t in app_data["teachers"]:
        if t["name"].lower() == name.lower() and t["speciality"].lower() == spec.lower():
            print(f"Teacher '{name}' with speciality '{spec}' already exists.")
            return
    t = {"id": app_data["next_teacher_id"], "name": name, "speciality": spec}
    app_data["next_teacher_id"] += 1
    app_data["teachers"].append(t)
    print(f"Teacher '{t['name']}' added (speciality: {t['speciality']}).")
    autosave()


def update_teacher(tid, new_name=None, new_spec=None):
    t = find_teacher_by_id(tid)
    if not t:
        print(f"No teacher with ID {tid}.")
        return
    if nonempty(new_name):
        t["name"] = new_name.strip()
    if nonempty(new_spec):
        t["speciality"] = norm(new_spec)
    print(f"Teacher [{tid}] updated.")
    autosave()


def remove_teacher(tid):
    t = find_teacher_by_id(tid)
    if not t:
        print(f"No teacher with ID {tid}.")
        return
    app_data["lesson_assignments"] = [
        a for a in app_data["lesson_assignments"] if a["teacher_id"] != tid]
    app_data["teachers"] = [x for x in app_data["teachers"] if x["id"] != tid]
    print(f"Teacher [{tid}] removed.")
    autosave()

# -------------------
# Listing & Searching
# -------------------


def list_students():
    print("\n--- Students ---")
    if not app_data["students"]:
        print("(none)")
        return
    for s in app_data["students"]:
        instruments = ", ".join(
            s["instruments"]) if s["instruments"] else "(no instruments)"
        print(f"[{s['id']}] {s['name']} → {instruments}")


def list_teachers():
    print("\n--- Teachers ---")
    if not app_data["teachers"]:
        print("(none)")
        return
    for t in app_data["teachers"]:
        print(f"[{t['id']}] {t['name']} (speciality: {t['speciality']})")


def find_students_by_name(term):
    needle = (term or "").strip().lower()
    print(f"\nSearch students: '{needle}'")
    res = [s for s in app_data["students"] if needle in s["name"].lower()]
    if not res:
        print("(no matches)")
        return
    for s in res:
        instruments = ", ".join(
            s["instruments"]) if s["instruments"] else "(no instruments)"
        print(f"- [{s['id']}] {s['name']} → {instruments}")


def find_teachers(term):
    needle = (term or "").strip().lower()
    print(f"\nSearch teachers: '{needle}'")
    res = [t for t in app_data["teachers"]
           if needle in t["name"].lower() or needle in t["speciality"].lower()]
    if not res:
        print("(no matches)")
        return
    for t in res:
        print(f"- [{t['id']}] {t['name']} (speciality: {t['speciality']})")


def front_desk_lookup(term):
    find_students_by_name(term)
    find_teachers(term)

# -------------------
# Extra A (Instrument insights)
# -------------------


def list_instruments_summary():
    counts = {}
    for s in app_data["students"]:
        for instr in s["instruments"]:
            counts[instr.lower()] = counts.get(instr.lower(), 0) + 1
    print("\n--- Instrument Summary ---")
    if not counts:
        print("(none)")
        return
    for instr in sorted(counts.keys()):
        print(f"{instr.title()} - {counts[instr]} student(s)")


def find_students_by_instrument(term):
    needle = (term or "").strip().lower()
    print(f"\nStudents learning '{needle}':")
    res = []
    for s in app_data["students"]:
        if any(needle in instr.lower() for instr in s["instruments"]):
            res.append(s)
    if not res:
        print("(no matches)")
        return
    for s in res:
        instruments = ", ".join(
            s["instruments"]) if s["instruments"] else "(no instruments)"
        print(f"- [{s['id']}] {s['name']} → {instruments}")

# -------------------
# Extra B (Teacher assignments)
# -------------------


def assign_teacher(sid, instrument, tid):
    s = find_student_by_id(sid)
    t = find_teacher_by_id(tid)
    if not s:
        print(f"No student with ID {sid}.")
        return
    if not t:
        print(f"No teacher with ID {tid}.")
        return
    instr = norm(instrument)
    if instr not in s["instruments"]:
        print(f"{s['name']} not enrolled in '{instr}'.")
        return
    if t["speciality"].lower() != instr.lower():
        print(
            f"Teacher '{t['name']}' speciality is '{t['speciality']}', not '{instr}'.")
        return
    # replace if exists
    app_data["lesson_assignments"] = [
        a for a in app_data["lesson_assignments"]
        if not (a["student_id"] == sid and a["instrument"] == instr.lower())
    ]
    app_data["lesson_assignments"].append(
        {"student_id": sid, "instrument": instr.lower(), "teacher_id": tid})
    print(f"Assigned {t['name']} → {s['name']} for {instr}.")
    autosave()


def view_assignments_for_student(sid):
    s = find_student_by_id(sid)
    if not s:
        print(f"No student with ID {sid}.")
        return
    print(f"\nAssignments for {s['name']}:")
    if not s["instruments"]:
        print("(no instruments)")
        return
    for instr in s["instruments"]:
        found = next((a for a in app_data["lesson_assignments"]
                      if a["student_id"] == sid and a["instrument"] == instr.lower()), None)
        if found:
            t = find_teacher_by_id(found["teacher_id"])
            print(
                f"{instr}: {t['name']} (ID {t['id']})" if t else f"{instr}: (teacher not found)")
        else:
            print(f"{instr}: (no teacher assigned)")

# -------------------
# Receptionist (check-in, print card)
# -------------------


def check_in(sid, course):
    s = find_student_by_id(sid)
    if not s:
        print(f"No student with ID {sid}.")
        return
    course_norm = norm(course)
    if course_norm not in s["instruments"]:
        print(f"{s['name']} not enrolled in '{course_norm}'.")
        return
    ts = datetime.datetime.now().isoformat(timespec="seconds")
    app_data["attendance"].append(
        {"student_id": sid, "course": course_norm, "timestamp": ts})
    print(f"Checked in: {s['name']} for {course_norm} at {ts}.")
    autosave()


def print_student_card(sid, outfile=None):
    s = find_student_by_id(sid)
    if not s:
        print(f"No student with ID {sid}.")
        return
    outfile = outfile or f"student_{sid}_card.txt"
    with open(outfile, "w", encoding="utf-8") as f:
        f.write(f"Student ID: {s['id']}\n")
        f.write(f"Name     : {s['name']}\n")
        f.write("Instruments: " +
                (", ".join(s["instruments"]) if s["instruments"] else "(none)") + "\n")
    print(f"Card printed to {outfile}")

# -------------------
# Extra (PST2): CSV Export
# -------------------


def export_csv(dir_path="exports"):
    try:
        os.makedirs(dir_path, exist_ok=True)
        # students
        with open(os.path.join(dir_path, "students.csv"), "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["id", "name", "instruments"])
            for s in app_data["students"]:
                w.writerow([s["id"], s["name"], "|".join(s["instruments"])])
        # teachers
        with open(os.path.join(dir_path, "teachers.csv"), "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["id", "name", "speciality"])
            for t in app_data["teachers"]:
                w.writerow([t["id"], t["name"], t["speciality"]])
        # attendance
        with open(os.path.join(dir_path, "attendance.csv"), "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["student_id", "course", "timestamp"])
            for a in app_data["attendance"]:
                w.writerow([a["student_id"], a["course"], a["timestamp"]])
        # assignments
        with open(os.path.join(dir_path, "lesson_assignments.csv"), "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["student_id", "instrument", "teacher_id"])
            for a in app_data["lesson_assignments"]:
                w.writerow([a["student_id"], a["instrument"], a["teacher_id"]])
        print(f"CSV reports exported in '{dir_path}/'")
    except Exception as e:
        print(f"CSV export failed: {e}")

# -------------------
# Main Menu
# -------------------


def main():
    load_data()
    while True:
        print("\n=== MSMS (PST2) ===")
        print("1. Add student")
        print("2. Enrol student in instrument")
        print("3. Add teacher")
        print("4. Update student")
        print("5. Update teacher")
        print("6. Remove student")
        print("7. Remove teacher")
        print("8. List students")
        print("9. List teachers")
        print("10. Lookup")
        print("11. Instrument summary")
        print("12. Find students by instrument")
        print("13. Assign teacher")
        print("14. View assignments for student")
        print("15. Check-in student")
        print("16. Print student card")
        print("17. Save now")
        print("18. Load from file")
        print("19. Export CSV reports")
        print("0. Exit")
        choice = input("Select: ").strip()

        try:
            if choice == "1":
                name = input("Student name: ")
                instr = input("First instrument (optional): ")
                add_student(name, instr)
            elif choice == "2":
                sid = int(input("Student ID: "))
                instr = input("Instrument: ")
                enrol_instrument(sid, instr)
            elif choice == "3":
                name = input("Teacher name: ")
                spec = input("Speciality: ")
                add_teacher(name, spec)
            elif choice == "4":
                sid = int(input("Student ID: "))
                new_name = input("New name (blank = skip): ")
                update_student(sid, new_name)
            elif choice == "5":
                tid = int(input("Teacher ID: "))
                new_name = input("New name (blank=skip): ")
                new_spec = input("New speciality (blank=skip): ")
                update_teacher(tid, new_name, new_spec)
            elif choice == "6":
                sid = int(input("Student ID: "))
                remove_student(sid)
            elif choice == "7":
                tid = int(input("Teacher ID: "))
                remove_teacher(tid)
            elif choice == "8":
                list_students()
            elif choice == "9":
                list_teachers()
            elif choice == "10":
                term = input("Search term: ")
                front_desk_lookup(term)
            elif choice == "11":
                list_instruments_summary()
            elif choice == "12":
                term = input("Instrument: ")
                find_students_by_instrument(term)
            elif choice == "13":
                sid = int(input("Student ID: "))
                instr = input("Instrument: ")
                tid = int(input("Teacher ID: "))
                assign_teacher(sid, instr, tid)
            elif choice == "14":
                sid = int(input("Student ID: "))
                view_assignments_for_student(sid)
            elif choice == "15":
                sid = int(input("Student ID: "))
                course = input("Course: ")
                check_in(sid, course)
            elif choice == "16":
                sid = int(input("Student ID: "))
                print_student_card(sid)
            elif choice == "17":
                save_data()
            elif choice == "18":
                load_data()
            elif choice == "19":
                folder = input(
                    "Export folder (default=exports): ").strip() or "exports"
                export_csv(folder)
            elif choice == "0":
                break
            else:
                print("Invalid option.")
        except ValueError:
            print("Invalid input (numeric ID expected).")


if __name__ == "__main__":
    main()
