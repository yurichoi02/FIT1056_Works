# --- Main Application ---
def main():
    """Runs the main interactive menu for the receptionist."""
    # Think of this as the 'control room' — where the program actually runs
    # and lets the front desk person interact with the system.

    # Pre-populate some data so we have teachers ready for testing
    add_teacher("Dr. Keys", "Piano")     # Teacher who teaches Piano
    add_teacher("Ms. Fret", "Guitar")    # Teacher who teaches Guitar

    while True:  # This loop keeps the menu running until the user chooses to quit
        print("\n===== Music School Front Desk =====")
        print("1. Register New Student")
        print("2. Enrol Existing Student")
        print("3. Lookup Student or Teacher")
        print("4. (Admin) List all Students")
        print("5. (Admin) List all Teachers")
        print("q. Quit")
        
        choice = input("Enter your choice: ")  # Get the user's menu selection

        if choice == '1':
            # Option 1: Register a brand new student
            name = input("Enter student name: ")
            instrument = input("Enter instrument to enrol in: ")
            front_desk_register(name, instrument)

        elif choice == '2':
            # Option 2: Enrol an already registered student
            try:
                student_id = int(input("Enter student ID: "))  # Must be a number
                instrument = input("Enter instrument to enrol in: ")
                front_desk_enrol(student_id, instrument)
            except ValueError:
                print("Invalid ID. Please enter a number.")

        elif choice == '3':
            # Option 3: Search for a student or teacher by keyword
            term = input("Enter search term: ")
            front_desk_lookup(term)

        elif choice == '4':
            # Option 4: Show all students (Admin feature)
            list_students()

        elif choice == '5':
            # Option 5: Show all teachers (Admin feature)
            list_teachers()

        elif choice.lower() == 'q':
            # Option Q: Quit the program
            print("Exiting program. Goodbye!")
            break  # Leave the loop, ending the program

        else:
            # If user types something not in the menu
            print("Invalid choice. Please try again.")

# --- Program Start ---
if __name__ == "__main__":
    # This ensures the main() function only runs if this file is run directly
    # (and not if it’s imported somewhere else).
    main()
