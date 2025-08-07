# Music School Management System (MSMS)

**FIT1056 – Introduction to Software Engineering**  
**Semester 2, 2025 — PST1: The In-Memory Prototype**

---

##  Project Overview

This is the first stage (PST1) of a multi-phase software engineering project. The goal is to create a basic Music School Management System (MSMS) that supports core functionalities using **in-memory data structures** only.

All logic is implemented in a single file (`MSMS.py`) and all data will be lost once the program stops — perfect for quick iteration and focusing on logic.

---

##  Features Implemented

### Fragment 1.1 – Data Structures
- `Student` class (ID, name, list of instruments)
- `Teacher` class (ID, name, specialty)
- `student_db` and `teacher_db` as in-memory "databases"
- Auto-incrementing ID counters

### Fragment 1.2 – Core Helper Functions
- `add_teacher(name, specialty)`
- `list_students()`, `list_teachers()`
- `find_students(term)`, `find_teachers(term)`

### Fragment 1.3 – Front Desk Functions
- `find_student_by_id(student_id)`
- `front_desk_register(name, instrument)`
- `front_desk_enrol(student_id, instrument)`
- `front_desk_lookup(term)`

### Fragment 1.4 – Main Menu Loop
- Interactive console menu using `while True`
- Accepts user input and runs front desk features

---

##  How to Run

1. Open Terminal and go to the project folder:
   ```bash
   cd /Users/choiyuri/Desktop/monash_works/FIT1056_Works/individual


