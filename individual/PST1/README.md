# Music School Management System (MSMS)

Monash University Malaysia
FIT1056 – Introduction to Software Engineering  
Semester 2, 2025 — PST1: The In-Memory Prototype

---

## Author Information
- Name: Choi Yuri 
- Student ID: 33705437
- Git Repository: https://github.com/yurichoi02/FIT1056_Works

---

## Project Overview

This is the first stage (PST1) of a multi-phase software engineering project. The goal is to develop a basic Music School Management System (MSMS) that supports core operations using in-memory data structures only.

The system logic is implemented in a single file (`MSMS.py`). Since this is an in-memory prototype, all data will be lost once the program stops. This allows the focus to be on functionality and logic design.

---

## Features Implemented

### Fragment 1.1 – Data Structures
- `Student` class (ID, name, list of instruments)
- `Teacher` class (ID, name, specialty)
- In-memory "databases": `student_db`, `teacher_db`
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
- Interactive console menu for receptionist role
- Accepts user input for registration, enrolment, and search

---

## How to Run

1. Open Terminal and navigate to the project folder:
   ```bash
   cd /Users/choiyuri/Desktop/monash_works/FIT1056_Works/individual/PST1

2. Run the Python program:
```bash
   Python3 MSMS.py