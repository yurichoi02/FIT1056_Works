# Music School Management System (MSMS) – PST4

**Monash University Malaysia**  
**FIT1056 – Introduction to Software Engineering**  
**Semester 2, 2025**

---

## Author Information
- **Name:** Choi Yuri  
- **Student ID:** 33705437  
- **Git Repository:** https://github.com/yurichoi02/FIT1056_Works

---

## Project Overview (MSMS – PST4)
This project is **PST4** of the Music School Management System (MSMS).  
It builds on the PST3 backend (User, Student, Teacher, Course and ScheduleManager) and integrates a **Streamlit GUI** for a receptionist/admin-facing application.

**What you can do**
- Register new students (**with timestamps**)
- View all students (ID, name, enrolled count, **registered_at**, **preferred instrument**)
- Search students by name
- Summarise enrolments by **instrument** (registered vs enrolled + number of courses)
- View **daily rosters**, sorted by start time, filterable by teacher
- **Check in** students with exact timestamps
- **Export attendance** to CSV (admin only)
- Basic **security**: 6-digit Admin PIN to protect admin controls

---

## How to Run

1) Create and activate a virtual environment
```bash
python3 -m venv .venv
source .venv/bin/activate      # Mac/Linux
# .venv\Scripts\activate       # Windows
```

2) Install dependencies
```bash
pip install streamlit pandas
```

3) Run the app
```bash
streamlit run msms.py
```
(If your editor shows “Import streamlit could not be resolved”, select the **.venv** interpreter or install `streamlit` into that environment.)

---

## PST4 Features Implemented
- **Completed TODOs** in `ScheduleManager`  
  - `_load_data()` loads students/teachers/courses/attendance from `data/msms.json`  
  - `_save_data()` persists changes back to JSON
- **Student management**  
  - `register_new_student(name, instrument)` with **registered_at** timestamp and auto-enrol if a matching instrument course exists  
  - `list_students()` returns table-friendly rows
- **Roster & Attendance**  
  - `daily_roster(day)` assembles rows for the selected weekday  
  - `check_in(student_id, course_id)` validates and appends an attendance record with a **timestamp** (returned to UI)
- **Extras for higher marks**  
  - `search_students(query)` (case-insensitive)  
  - `instrument_summary()` shows **registered_students**, **enrolled_students**, and **courses** per instrument  
  - **Teacher filter** on the roster table  
  - **Attendance CSV export** (`attendance_csv()`)  
  - **Instrument dropdown** on registration (from existing courses)  
  - **Edit/Delete** for students & courses (confirm checkbox + auto-refresh)  
  - **Teacher Management page** (Option B): **add teacher**, **add course**, **edit/delete teacher**, **edit/delete course**, **reassign course teacher**  
  - **Student Management** now focuses on: register/search students, instrument summary, **enrol student**, **edit/delete student**

---

## Security (Admin PIN)
PST4 is primarily for **receptionist/admin** use. Admin-only actions are gated by a **6-digit PIN**.

- **Default PIN** is **`123456`**.  
- For better security, set your own PIN via `.streamlit/secrets.toml` (recommended):

```toml
[general]
ADMIN_PIN = "987654"
```

### How it works
- In the **sidebar**, expand **Sign in** and enter the 6-digit PIN.  
- If correct, your role becomes `admin`; otherwise you remain `guest`.  
- **Admin-only controls**:
  - *Student Management* → **Enroll student**, **Edit/Delete student**
  - *Teacher Management* → **Add/Edit/Delete teacher**, **Add/Edit/Delete course**, **Reassign course teacher**
  - *Daily Roster* → **Export attendance**

Guests see a friendly info message instead.

> **Note:** If you do **not** provide a `secrets.toml`, the system will always use the default PIN `123456`.

---

## Demo Workflow
1. **Sign in as Admin** (sidebar → Sign in → enter 6-digit PIN).  
2. **Add teacher** (e.g., “Ms. Viola Chen – Violin”) from **Teacher Management → Add Teacher**.  
3. **Add course** (e.g., “Violin Foundations”) from **Teacher Management → Add Course** → pick day/time/room.  
4. **Register student** on **Student Management** (instrument dropdown includes any instruments with courses).  
5. **Enroll student into course** on **Student Management**.  
6. **Edit/Delete** students on **Student Management** (with “I’m sure” confirmation).  
7. **Edit/Delete** courses and **Edit/Delete** teachers on **Teacher Management**; **Reassign course teacher** if needed.  
8. **View roster** for the appropriate day; use **teacher filter** if needed.  
9. **Check in** the student → success toast shows **timestamp**.  
10. **Export attendance** (admin only) from **Daily Roster**.

---

## Project Structure
```
app/
  ├─ __init__.py
  ├─ user.py          # Base User class
  ├─ student.py       # StudentUser (preferred_instrument + registered_at)
  ├─ teacher.py       # TeacherUser + Course
  └─ schedule.py      # ScheduleManager (logic, persistence, extras, validation)
gui/
  ├─ main_dashboard.py   # Nav + 6-digit Admin PIN gate
  ├─ student_pages.py    # Register/search, summary, Enrol, Edit/Delete students
  ├─ teacher_pages.py    # Add/Edit/Delete teacher, Add/Edit/Delete course, Reassign
  └─ roster_pages.py     # Daily roster, check-in, export (admin-only)
data/
  └─ msms.json        # Sample data (students, teachers, courses, lessons, attendance)
main.py               # Entry point (Streamlit)
README_PST4.md        # This file
```

---

## Notes
- Time input validated as **HH:MM (24-hour)** when creating/editing a course.
- Duplicate teacher names and course names are blocked.
- Teacher **day/time** slot conflicts are blocked (create/edit/reassign).
- Payments page is a **stub** (planned for PST5).