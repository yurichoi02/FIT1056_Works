# main.py — PST3 view layer (thin CLI)
from app.schedule import ScheduleManager


def front_desk_daily_roster(manager: ScheduleManager, day: str):
    roster = manager.get_daily_roster(day)
    print(f"\n=== Daily Roster for {day.title()} ===")
    if not roster:
        print("(no lessons)")
        return
    for r in roster:
        print(f"- {r['start_time']}  {r['course_name']} [{r['instrument']}] "
              f"with {r['teacher']} in {r['room']} (Course ID {r['course_id']})")


def student_schedule_lookup(manager: ScheduleManager):
    try:
        sid = int(input("Student ID: ").strip())
        items = manager.get_student_schedule(sid)
        print(f"\n=== Schedule for Student {sid} ===")
        if not items:
            print("(no courses/lessons)")
            return
        for it in items:
            print(f"- {it['day']:>10}  {it['start_time']:>5}  {it['course_name']} "
                  f"[{it['instrument']}] with {it['teacher']}  {it['room']}")
    except ValueError as e:
        print(e)


def enrol_student(manager: ScheduleManager):
    try:
        sid = int(input("Student ID: ").strip())
        cid = int(input("Course ID: ").strip())
        manager.enrol_student_to_course(sid, cid)
        print("Enrolment complete.")
    except ValueError as e:
        print(e)


def do_check_in(manager: ScheduleManager):
    try:
        sid = int(input("Student ID: ").strip())
        cid = int(input("Course ID: ").strip())
        ts = manager.check_in(sid, cid)
        print(f"Checked in at {ts}.")
    except ValueError as e:
        print(e)


def reassign_course_teacher(manager: ScheduleManager):
    try:
        cid = int(input("Course ID: ").strip())
        tid = int(input("New Teacher ID: ").strip())
        manager.reassign_teacher(cid, tid)
        print("Teacher reassigned.")
    except ValueError as e:
        print(e)


def list_students(manager: ScheduleManager):
    print("\n--- Students ---")
    for s in manager.students:
        print(f"[{s.id}] {s.name} → {s.enrolled_course_ids or '()'}")


def list_teachers(manager: ScheduleManager):
    print("\n--- Teachers ---")
    for t in manager.teachers:
        print(f"[{t.id}] {t.name} (speciality: {t.speciality})")


def instrument_summary(manager: ScheduleManager):
    print("\n--- Instrument Summary ---")
    m = manager.instrument_summary()
    if not m:
        print("(none)")
        return
    for instr in sorted(m.keys()):
        print(f"{instr}: {m[instr]} student(s)")


def find_students_by_instrument(manager: ScheduleManager):
    term = input("Instrument term: ").strip()
    res = manager.find_students_by_instrument(term)
    print(f"\nStudents learning ~{term}~")
    if not res:
        print("(no matches)")
        return
    for s in res:
        print(f"- [{s.id}] {s.name}")


def main():
    mgr = ScheduleManager()  # loads data/msms.json
    while True:
        print("\n=== MSMS (PST3) ===")
        print("1. Daily roster by day")
        print("2. Student schedule lookup")
        print("3. Enrol student in course")
        print("4. Check-in student")
        print("5. Reassign course teacher")
        print("6. List students")
        print("7. List teachers")
        print("8. Instrument summary")
        print("9. Find students by instrument")
        print("s. Save")
        print("q. Quit")
        choice = input("Select: ").strip().lower()

        if choice == "1":
            day = input("Day (e.g., Monday): ")
            front_desk_daily_roster(mgr, day)
        elif choice == "2":
            student_schedule_lookup(mgr)
        elif choice == "3":
            enrol_student(mgr)
        elif choice == "4":
            do_check_in(mgr)
        elif choice == "5":
            reassign_course_teacher(mgr)
        elif choice == "6":
            list_students(mgr)
        elif choice == "7":
            list_teachers(mgr)
        elif choice == "8":
            instrument_summary(mgr)
        elif choice == "9":
            find_students_by_instrument(mgr)
        elif choice == "s":
            mgr._save_data()  # manual save (mutations already autosave)
            print("Saved.")
        elif choice == "q":
            break
        else:
            print("Invalid option.")


if __name__ == "__main__":
    main()
