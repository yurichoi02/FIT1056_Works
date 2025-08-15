# Fragment2_4.py
# Main menu loop for MSMS

from MSMS import app_data, load_data, save_data
from Fragment2_2 import (
    add_teacher, update_teacher, remove_teacher,
    add_student, update_student, remove_student
)
from Fragment2_3 import check_in, print_student_card, read_int, read_str

def main():
    load_data()

    while True:
        print("\n--- Music School Management System ---")
        print("1. Add Teacher")
        print("2. Update Teacher")
        print("3. Remove Teacher")
        print("4. Add Student")
        print("5. Update Student")
        print("6. Remove Student")
        print("7. Check-in Student")
        print("8. Print Student Card")
        print("9. View All Data")
        print("0. Exit")

        choice = read_int("Enter choice: ")

        if choice == 1:
            name = read_str("Teacher name: ")
            speciality = read_str("Speciality: ")
            add_teacher(name, speciality)

        elif choice == 2:
            tid = read_int("Teacher ID to update: ")
            name = read_str("New name (leave blank to skip): ") or None
            speciality = read_str("New speciality (leave blank to skip): ") or None
            update_teacher(tid, name, speciality)

        elif choice == 3:
            tid = read_int("Teacher ID to remove: ")
            remove_teacher(tid)

        elif choice == 4:
            name = read_str("Student name: ")
            instrument = read_str("Instrument: ")
            add_student(name, instrument)

        elif choice == 5:
            sid = read_int("Student ID to update: ")
            name = read_str("New name (leave blank to skip): ") or None
            instrument = read_str("New instrument (leave blank to skip): ") or None
            update_student(sid, name, instrument)

        elif choice == 6:
            sid = read_int("Student ID to remove: ")
            remove_student(sid)

        elif choice == 7:
            sid = read_int("Student ID to check-in: ")
            check_in(sid)

        elif choice == 8:
            sid = read_int("Student ID to print card: ")
            print_student_card(sid)

        elif choice == 9:
            print("\nTeachers:", app_data["teachers"])
            print("Students:", app_data["students"])

        elif choice == 0:
            save_data()
            break
        else:
            print("Invalid choice.")

if __name__ == "__main__":
    main()
