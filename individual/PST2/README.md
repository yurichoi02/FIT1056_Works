# Music School Management System (MSMS)

FIT1056 – Introduction to Software Engineering  
Semester 2, 2025 — PST1 & PST2

---

## Author
- Name: Choi Yuri
- Student ID: 33705437

---

## PST1 — In-Memory Prototype

### Features
- `Student` and `Teacher` data classes (in-memory only)
- Register new students and enrol them in instruments
- Add teachers with a speciality
- Search students and teachers
- Simple console menu (text-based)
- **Extras (PST1):**
  - Instrument summary & search by instrument
  - Assign teacher per instrument + view assignments

### How to run
```bash
python3 MSMS.py
```

---

## PST2 — JSON Persistence & CRUD Upgrade

### What changed
- Data now stored in `msms.json`
- Loads automatically at startup
- Saves after every change (auto-save)
- **Full CRUD:**
  - Students: add, update (name), remove, enrol instrument
  - Teachers: add, update (name/speciality), remove
- **Receptionist features:**
  - Check-in a student (records timestamp + instrument)
  - Print student card to a text file
- **Extras (PST2):**
  - Export CSV reports (students, teachers, attendance, assignments)

### How to run
You can run either:
```bash
python3 Fragment2_4.py
```
or directly:
```bash
python3 MSMS.py
```

### Menu (PST2)
```
1. Add student
2. Enrol student in instrument
3. Add teacher
4. Update student
5. Update teacher
6. Remove student
7. Remove teacher
8. List students
9. List teachers
10. Lookup
11. Instrument summary
12. Find students by instrument
13. Assign teacher
14. View assignments for student
15. Check-in student
16. Print student card
17. Save now
18. Load from file
19. Export CSV reports
0. Exit
```
