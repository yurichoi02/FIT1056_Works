# main.py — PST3 view layer (thin CLI)
import sys
from app import ScheduleManager  # clean import thanks to __init__.py


def front_desk_daily_roster(manager, day):
    """Prints all lessons scheduled for a given day."""
    roster = manager.get_daily_roster(day)
    if not roster:
        print(f"No lessons scheduled for {day}.")
        return
    print(f"\n=== Daily Roster for {day} ===")
    for lesson in roster:
        print(
            f"- {lesson['start_time']}  {lesson['course_name']} [{lesson['instrument']}] "
            f"with {lesson['teacher_name']} in {lesson['room']} (Course ID {lesson['course_id']})"
        )


def front_desk_student_schedule(manager, student_id):
    """Prints a student's full timetable with teachers and rooms."""
    schedule = manager.get_student_schedule(student_id)
    if not schedule:
        print("No schedule found.")
        return
    print(f"\n=== Schedule for {schedule['student_name']} ===")
    for item in schedule["courses"]:
        print(
            f"- {item['course_name']} ({item['instrument']}) with {item['teacher_name']}"
        )
        for lesson in item["lessons"]:
            print(
                f"    {lesson['day']} {lesson['start_time']} in {lesson['room']} "
                f"(Lesson ID {lesson['lesson_id']})"
            )


def main():
    manager = ScheduleManager()

    menu = """
=== MSMS (PST3) ===
1. Daily roster by day
2. Student schedule lookup
3. Enrol student in course
4. Check-in student
5. Reassign course teacher
6. List students
7. List teachers
8. Instrument summary
9. Find students by instrument
s. Save
q. Quit
"""
    while True:
        print(menu)
        choice = input("Select: ").strip()

        if choice == "1":
            day = input("Day (e.g., Monday): ").strip()
            front_desk_daily_roster(manager, day)

        elif choice == "2":
            try:
                student_id = int(input("Enter student ID: "))
                front_desk_student_schedule(manager, student_id)
            except ValueError:
                print("Invalid input. Student ID must be a number.")

        elif choice == "3":
            try:
                student_id = int(input("Enter student ID: "))
                course_id = int(input("Enter course ID: "))
                manager.enrol_student_in_course(student_id, course_id)
                print("Student enrolled successfully.")
            except ValueError as e:
                print(f"Error: {e}")

        elif choice == "4":
            try:
                student_id = int(input("Enter student ID: "))
                course_id = int(input("Enter course ID: "))
                manager.check_in(student_id, course_id)
            except ValueError as e:
                print(f"Error: {e}")

        elif choice == "5":
            try:
                course_id = int(input("Enter course ID: "))
                teacher_id = int(input("Enter new teacher ID: "))
                manager.reassign_teacher(course_id, teacher_id)
                print("Teacher reassigned successfully.")
            except ValueError as e:
                print(f"Error: {e}")

        elif choice == "6":
            manager.list_students()

        elif choice == "7":
            manager.list_teachers()

        elif choice == "8":
            manager.instrument_summary()

        elif choice == "9":
            term = input("Enter instrument: ").strip()
            manager.find_students_by_instrument(term)

        elif choice.lower() == "s":
            manager._save_data()
            print("Data saved manually.")

        elif choice.lower() == "q":
            print("Goodbye!")
            sys.exit(0)

        else:
            print("Invalid choice. Try again.")


if __name__ == "__main__":
    main()
