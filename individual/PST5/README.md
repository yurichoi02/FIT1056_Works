# Music School Management System (MSMS) – PST5

**Monash University Malaysia**  
**FIT1056 – Introduction to Software Engineering**  
**Semester 2, 2025**

---

## Author Information
- **Name:** Choi Yuri  
- **Student ID:** 33705437  
- **Git Repository:** https://github.com/yurichoi02/FIT1056_Works

---

## Project Overview (MSMS – PST5)

This release extends PST4 with **finance**, **logging**, **data backups**, and an **automated test suite**.  
It remains a receptionist/admin-facing Streamlit app built on a clean separation of **GUI** and **business logic** (`ScheduleManager`).

### What’s New in PST5
- **Finance & Reporting**
  - `record_payment(student_id, amount, method)` — normalized methods (`cash`, `card`, `transfer`, `ewallet`) with friendly synonyms
  - `get_payment_history(student_id)`
  - `export_report(kind, out_path)` → CSV for **finance** or **attendance**
- **Logging**
  - Centralized logging via `admin_utils.init_logger()` (file **+** console) with daily rotation
- **Lesson Cancellation**
  - `cancel_lesson(lesson_id, reason)` sets `cancelled` and stores the reason
- **Backups**
  - `backup_data()` creates timestamped copies of `data/msms.json` in `data/backups/`
  - **“Backup Now”** sidebar button (admin-only)
- **Automated Tests**
  - Pytest suite validating finance, cancellation, and CSV export
- **Admin-only Pages**
  - **Payments** and **System Logs** are visible only to admins

PST4 capabilities remain: student/teacher/course management, roster, attendance, JSON persistence, and a Streamlit GUI with an admin PIN gate.

---

## How to Run

1) Create and activate a virtual environment:
```bash
python3 -m venv .venv
# macOS/Linux:
source .venv/bin/activate
# Windows (PowerShell):
# .venv\Scripts\Activate.ps1
```

2) Install dependencies:
```bash
pip install streamlit pandas pytest
```

3) Ensure folders exist (auto-created at runtime if missing):
```bash
mkdir -p data/backups logs
```

4) Launch the app **via the top-level launcher** (initializes logging and does a safe backup first):
```bash
streamlit run msms.py
```

---

## Security (Admin PIN)

Admin-only actions are gated by a **6-digit PIN**.

- **Default PIN:** `123456` (for this project)
- To change, configure either:
  - `.streamlit/secrets.toml`
    ```toml
    ADMIN_PIN = "654321"
    ```
  - or environment variable:
    ```bash
    export ADMIN_PIN=654321
    ```

**Where it’s used:** sidebar → **Sign in**. On correct PIN, role becomes `admin`; otherwise `guest`. Admins can access protected controls (Payments, System Logs, **Backup Now**, and any destructive actions).

---

## Using the GUI

**Navigation (sidebar):**
- **Student Management** – register/search students, instrument summary, enrol student, edit/delete
- **Teacher Management** – add/edit/delete teacher, add/edit/delete course, reassign teacher
- **Daily Roster** – view roster by weekday, optional teacher filter, **check-in** with timestamp
- **Payments** *(admin only)* – record payments; view per-student history, recent payments, method breakdown; CSV download + optional on-disk export
- **System Logs** *(admin only)* – tail, filter, download, and clear `logs/msms.log`

**Admin Tools (sidebar expander):**
- **Backup Now** – triggers `backup_data()` to create a timestamped JSON backup

---

## Architecture & Project Structure

```
app/
  ├─ schedule.py           # Core logic (students/teachers/courses/attendance/finance + atomic save/backups hooks)
  ├─ admin_utils.py        # init_logger() (daily rotating), backup_data()
  ├─ student.py            # StudentUser model
  └─ teacher.py            # TeacherUser, Course models
gui/
  ├─ main_dashboard.py     # Streamlit navigation, PIN gate, admin-only pages, “Backup Now” button
  ├─ finance_pages.py      # Finance UI (record payment, history, recent payments, method breakdown, CSV download)
  ├─ logs_page.py          # Admin-only log viewer (tail, filter, download, clear)
  ├─ student_pages.py      # Student management UI
  ├─ teacher_pages.py      # Teacher management UI
  └─ roster_pages.py       # Roster & attendance UI
data/
  ├─ msms.json             # Main data store (auto-created)
  └─ backups/              # Timestamped backups (auto-created)
logs/
  └─ msms.log              # Application logs (rotated daily; auto-created)
tests/
  └─ test_schedule_manager.py  # Pytest suite for PST5 features
msms.py                    # Launcher: init_logger → backup_data → launch GUI
README.md                  # This file
```

> Note: Core manager lives in `app/schedule.py`.

---

## Design Choices & Assumptions

- **JSON persistence** with **atomic writes** and automatic timestamped backups (protects against partial writes)
- **Validation-first**:
  - Payment amount handled as precise `Decimal` (stored as string in JSON)
  - Payment **method normalization** (friendly labels allowed; stored canonical value)
  - Time parsing for roster sorting (`HH:MM`, 24h)
  - Check-in requires valid enrolment
- **Single slot per course** (per PST scope); cancellation marks that slot
- **Admin PIN**: single shared PIN model acceptable for this assignment
- **Logging**: daily rotating file + console ensuring readable logs and bounded file size

---

## Data & Logs

- **Data**: `data/msms.json`  
  Loaded/saved by `ScheduleManager._load_data()` / `_save_data()` with **atomic replace** and timestamped backups.

- **Backups**: `data/backups/backup_YYYY-MM-DD_HH-MM-SS.json`  
  Created at app start (via `msms.py`) and via **Backup Now**. Uses timestamped filenames.

- **Logs**: `logs/msms.log`  
  Daily-rotating logs. Records INFO/WARNING/ERROR events (registration, payments, exports, cancellations, errors). View/manage via **System Logs** page.

---

## Testing

1) Run tests:
```bash
pytest -v
```

2) What’s covered:
- Payment lifecycle (`record_payment`, `get_payment_history`)
- Finance CSV export (`export_report("finance", path)`)
- Attendance CSV export (`export_report("attendance", path)`)
- Lesson cancellation (`cancel_lesson`)
- Edge cases: unknown student history, invalid report kind, input validation

Tests use a temporary data file (`tmp_path`) so real data isn’t touched.

---

## Demo Workflow (Suggested)

1. **Sign in as Admin** (sidebar → Sign in → enter 6-digit PIN)  
2. **Add teacher** (Teacher Management → Add Teacher)  
3. **Add course** (Teacher Management → Add Course → set day/time/room)  
4. **Register student** (Student Management → instrument dropdown populated from courses)  
5. **Enrol** student to course (Student Management)  
6. **View roster** (Daily Roster for the course’s day)  
7. **Check in** student (timestamp logged)  
8. **Payments** → record a payment and view history / recent payments / method breakdown  
9. **Export** finance/attendance via in-app CSV download (and optional on-disk export)  
10. **Backup Now** (sidebar → Admin Tools)  
11. **System Logs** (admin) → filter/tail/download/clear logs

---

## Quick Commands

**Run GUI**
```bash
streamlit run msms.py
```

**Run tests**
```bash
pytest -v
```

**Export finance report (example)**
```python
from app.schedule import ScheduleManager
m = ScheduleManager()
m.export_report("finance", "data/finance_report.csv")
```