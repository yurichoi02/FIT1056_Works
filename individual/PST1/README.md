# Music School Management System (MSMS)

FIT1056 – Introduction to Software Engineering  
Semester 2, 2025 — PST1

---

## Author
- Name: Choi Yuri
- Student ID: 33705437

---

## Overview
This is the first stage of a multi-phase project. PST1 builds an **in-memory** prototype of a Music School Management System.  
All data lives in memory and resets when the program ends.

Main, runnable code is in **MSMS.py**. The `Fragment*.py` files are **templates** that show what was covered in each fragment; the implementations are in `MSMS.py`.

---

## Features

### Fragment 1.1 – Data Structures
- `Student` and `Teacher` classes
- In-memory lists: `student_db`, `teacher_db`
- Auto-increment IDs for students and teachers

### Fragment 1.2 – Core Helper Functions
- `add_teacher(name, speciality)`
- `list_students()`, `list_teachers()`
- `find_students(term)`, `find_teachers(term)`

### Fragment 1.3 – Front Desk Functions
- `find_student_by_id(student_id)`
- `front_desk_register(name, instrument)`
- `front_desk_enrol(student_id, instrument)`
- `front_desk_lookup(term)`

### Fragment 1.4 – Main Menu
- Console menu tying everything together

---

## Extra Functionality (PST1)
1) **Instrument summary and search**
- `list_instruments_summary()` → shows each instrument and how many students learn it.
- `find_students_by_instrument(term)` → search students by instrument (case-insensitive).

2) **Assign teachers to students**
- `assign_teacher(student_id, instrument, teacher_id)` → assign if speciality matches and the student is enrolled.
- `view_assignments_for_student(student_id)` → view a student’s instruments and assigned teachers.

---

## How to Run
```bash
python3 MSMS.py
```

### Menu (PST1)
```
1. Register new student (and enrol in an instrument)
2. Enrol existing student in another instrument
3. Add teacher
4. List students
5. List teachers
6. Lookup (students & teachers)
7. Instrument summary
8. Find students by instrument
9. Assign teacher to student (by instrument)
10. View a student's teacher assignments
0. Exit
```