# Music School Management System (MSMS)

A simple management system for a music school, built step-by-step for **FIT1056 – Introduction to Software Engineering**.  
This is **PST3**, where the project moves from procedural scripts into a proper **OOP design** with models, a controller, and a clean view layer.

---

## Author
- Name: Choi Yuri  
- Student ID: 33705437  

---

## Project Structure
```
PST3/
 ├─ app/
 │   ├─ init.py        # marks app as a package, re-exports key classes
 │   ├─ user.py        # base User class
 │   ├─ student.py     # StudentUser class
 │   ├─ teacher.py     # TeacherUser + Course
 │   └─ schedule.py    # ScheduleManager (brain of system)
 ├─ data/
 │   └─ msms.json      # storage for all data
 ├─ Fragment3_3.py     # snippet for check-in method
 ├─ main.py            # console UI (view layer)
 └─ README.md
```

---

## What changed from PST2
- Refactored into a clean **Object-Oriented architecture**  
- Added dedicated classes: `User`, `StudentUser`, `TeacherUser`, `Course`  
- Central **ScheduleManager** now handles:
  - JSON load/save
  - Attendance log
  - Enrolments, lookups, assignments  
- `main.py` is now just the **view** → it shows menus and delegates to ScheduleManager  

---

## Core Features
- Add students, teachers, and courses  
- Enrol students in courses  
- Check-in students with timestamp (attendance tracking)  
- Instrument summary and search by instrument  
- Reassign teacher to course (speciality must match)  
- View assignments for a student  

---

## Extras (PST3)
✨ **Daily roster by day** — see all lessons grouped by time/room  
✨ **Student schedule lookup** — view a student’s full timetable with teachers  

(both extras go beyond the PDF requirements, but make the app more practical)  

---

## How to Run
From inside the `PST3` folder:
```bash
python3 MSMS.py
```

---

## Menu (PST3)
```
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
```

---

## Sample Run
```
=== MSMS (PST3) ===
1. Daily roster by day
2. Student schedule lookup
...
Select: 1
Day (e.g., Monday): Monday

=== Daily Roster for Monday ===
- 16:00  Beginner Piano [Piano] with Dr. Evelyn Keys in Room A (Course ID 101)
```

---

## Notes
- Learned how to separate logic into **Model, Controller, View**  
- JSON auto-saves after every change (so data isn’t lost)  
- Kept PST2 extras:
  - Assign teacher per instrument (now reassign course teacher in OOP)
  - Instrument summary & search by instrument
  - View assignments for a student  
- Added new extras in PST3:
  - Daily roster by day
  - Student schedule lookup  
- This redesign makes it easier to add more complex features later

