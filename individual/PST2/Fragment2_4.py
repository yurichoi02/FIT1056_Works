# --- Main Application Loop ---

def main():
    """Run the Music School Management System."""
    load_data()

    while True:
        print("\n===== MSMS v2 =====")
        print("1. Check-in Student")
        print("2. Print Student Card")
        print("3. Update Teacher Info")
        print("4. Remove Student")
        print("q. Quit")

        choice = input("Choose an option: ").strip().lower()
        made_change = False

        if choice == "1":
            sid = read_int("Student ID: ")
            cid = read_str("Course ID: ")
            check_in(sid, cid)
            made_change = True

        elif choice == "2":
            sid = read_int("Student ID to print: ")
            print_student_card(sid)

        elif choice == "3":
            tid = read_int("Teacher ID to update: ")
            new_name = read_str("New name (leave blank to skip): ", allow_empty=True)
            new_spec = read_str("New speciality (leave blank to skip): ", allow_empty=True)
            update_teacher(tid, name=new_name, speciality=new_spec)
            made_change = True

        elif choice == "4":
            sid = read_int("Student ID to remove: ")
            remove_student(sid)
            made_change = True

        elif choice == "q":
            print("Saving and exiting...")
            save_data()
            break

        else:
            print("Invalid option.")

        if made_change:
            save_data()


# --- Program Start ---
if __name__ == "__main__":
    main()