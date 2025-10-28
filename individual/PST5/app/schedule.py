from __future__ import annotations

import os
import re
import csv
import json
import shutil
import logging
import tempfile
from datetime import datetime, time
from decimal import Decimal, InvalidOperation
from json import JSONDecodeError

from app.student import StudentUser
from app.teacher import TeacherUser, Course

logger = logging.getLogger("msms")


class ScheduleManager:
    """
    Core data/service layer for MSMS.

    Key PST5 additions:
      - Finance log with precise Decimal amounts (stored as strings for JSON)
      - CSV export (finance/attendance) with basic CSV injection mitigation
      - Centralized logging (no prints)
      - Atomic JSON writes with timestamped backups
      - Payment method normalization (case-insensitive + synonyms)
    """

    # Canonical payment methods we store
    ACCEPTED_METHODS = {"cash", "card", "transfer", "ewallet"}

    # Common aliases/synonyms → normalized canonical method
    METHOD_ALIASES = {
        # cash
        "cash": "cash",

        # card
        "card": "card",
        "credit": "card",
        "credit card": "card",
        "debit": "card",
        "debit card": "card",

        # bank transfer
        "transfer": "transfer",
        "bank transfer": "transfer",
        "online banking": "transfer",
        "ibg": "transfer",
        "duitnow": "transfer",

        # ewallets (examples incl. Malaysia)
        "ewallet": "ewallet",
        "e-wallet": "ewallet",
        "e wallet": "ewallet",
        "tng": "ewallet",
        "touch n go": "ewallet",
        "touch 'n go": "ewallet",
        "grabpay": "ewallet",
        "boost": "ewallet",
        "shopeepay": "ewallet",
    }

    def __init__(self, data_path: str = "data/msms.json"):
        self.data_path = data_path
        self.students: list[StudentUser] = []
        self.teachers: list[TeacherUser] = []
        self.courses: list[Course] = []
        self.attendance_log: list[dict] = []
        self.finance_log: list[dict] = []   # PST5: finance events
        self.next_lesson_id: int = 1
        self._load_data()

    # ---------- Persistence & Safety ----------
    def _backup_path(self) -> str:
        ts = datetime.now().strftime("%Y%m%d-%H%M%S")
        base, ext = os.path.splitext(self.data_path)
        return f"{base}.bak.{ts}{ext}"

    def _atomic_write(self, payload: dict) -> None:
        """
        Safely write JSON data with:
         1) write to temp file
         2) make timestamped backup of old data
         3) atomic replace
        """
        # Ensure directory exists
        os.makedirs(os.path.dirname(self.data_path) or ".", exist_ok=True)

        # 1) Write to a temporary file
        dir_ = os.path.dirname(self.data_path) or "."
        with tempfile.NamedTemporaryFile(
            "w", delete=False, dir=dir_, encoding="utf-8", newline=""
        ) as tmp:
            json.dump(payload, tmp, indent=2)
            tmp_path = tmp.name

        # 2) Backup current (if exists)
        if os.path.exists(self.data_path):
            shutil.copy2(self.data_path, self._backup_path())

        # 3) Replace atomically
        os.replace(tmp_path, self.data_path)

    def _save_data(self) -> None:
        """
        Dump all in-memory structures to disk.
        Uses atomic write for safety.
        """
        data_to_save = {
            "students": [s.to_dict() for s in self.students],
            "teachers": [t.to_dict() for t in self.teachers],
            "courses": [c.to_dict() for c in self.courses],
            "attendance": list(self.attendance_log),
            "finance": list(self.finance_log),
        }
        self._atomic_write(data_to_save)
        logger.info("Data saved.")

    def _load_data(self) -> None:
        """
        Load existing data file if valid.
        If missing or corrupted, start with clean but log what happened.
        """
        try:
            with open(self.data_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except FileNotFoundError:
            logger.warning("Data file not found. Starting fresh dataset.")
            self.students = []
            self.teachers = []
            self.courses = []
            self.attendance_log = []
            self.finance_log = []
            return
        except JSONDecodeError:
            logger.error(
                "Data file corrupted or invalid JSON. Starting fresh dataset (backup preserved)."
            )
            self.students = []
            self.teachers = []
            self.courses = []
            self.attendance_log = []
            self.finance_log = []
            return

        self.students = [StudentUser.from_dict(
            d) for d in data.get("students", [])]
        self.teachers = [TeacherUser.from_dict(
            d) for d in data.get("teachers", [])]
        self.courses = [Course.from_dict(d) for d in data.get("courses", [])]
        self.attendance_log = list(data.get("attendance", []))
        self.finance_log = list(data.get("finance", []))

        # Track next_lesson_id by scanning lessons in courses
        max_id = 0
        for c in self.courses:
            for les in getattr(c, "lessons", []):
                try:
                    max_id = max(max_id, int(les.get("lesson_id", 0)))
                except Exception:
                    pass
        self.next_lesson_id = max_id + 1

    # ---------- Finders ----------
    def find_student_by_id(self, sid: int | str):
        try:
            sid = int(sid)
        except (TypeError, ValueError):
            return None
        return next((s for s in self.students if s.id == sid), None)

    def find_teacher_by_id(self, tid: int | str):
        try:
            tid = int(tid)
        except (TypeError, ValueError):
            return None
        return next((t for t in self.teachers if t.id == tid), None)

    def find_course_by_id(self, cid: int | str):
        try:
            cid = int(cid)
        except (TypeError, ValueError):
            return None
        return next((c for c in self.courses if c.id == cid), None)

    # ---------- Student Management / Registration ----------
    def _next_student_id(self) -> int:
        return max((s.id for s in self.students), default=0) + 1

    def register_new_student(self, name: str, instrument: str):
        """
        Create a new student record.
        Auto-enrol them if we already have a course for that instrument.
        """
        name, instrument = (name or "").strip(), (instrument or "").strip()
        if not name or not instrument:
            logger.warning("Register student rejected: empty name/instrument.")
            return None

        sid = self._next_student_id()
        student = StudentUser(
            sid,
            name,
            enrolled_course_ids=[],
            preferred_instrument=instrument,
        )
        student.registered_at = datetime.now().isoformat(timespec="seconds")

        # Auto-enrol if a matching instrument course exists
        match = next(
            (c for c in self.courses if c.instrument.lower() == instrument.lower()),
            None,
        )
        if match:
            student.enrolled_course_ids.append(match.id)
            match.enrolled_student_ids.append(sid)

        self.students.append(student)
        self._save_data()
        logger.info("New student registered: %s (ID %s)", name, sid)
        return sid

    def list_students(self) -> list[dict]:
        """
        Lightweight summary for UI tables.
        """
        return [
            {
                "id": s.id,
                "name": s.name,
                "enrolled": len(s.enrolled_course_ids),
                "registered_at": getattr(s, "registered_at", "N/A"),
                "preferred_instrument": getattr(s, "preferred_instrument", "-"),
            }
            for s in self.students
        ]

    # ---------- Roster & Attendance ----------
    @staticmethod
    def _parse_time(t: str | None) -> time:
        """
        Parse "HH:MM" into a time object for sorting.
        If invalid, return time.max so broken entries float to the end.
        """
        try:
            h, m = map(int, (t or "").split(":"))
            return time(h, m)
        except Exception:
            return time.max  # push malformed times to end

    def daily_roster(self, day: str) -> list[dict]:
        """
        Build a list of today's lessons with teacher + enrolled students.
        """
        rows = []
        day_norm = (day or "").lower()
        for c in self.courses:
            teacher = self.find_teacher_by_id(c.teacher_id)
            for les in getattr(c, "lessons", []):
                if (les.get("day", "") or "").lower() == day_norm:
                    student_names = [
                        self.find_student_by_id(sid).name
                        for sid in c.enrolled_student_ids
                        if self.find_student_by_id(sid)
                    ]
                    rows.append(
                        {
                            "course_id": c.id,
                            "course_name": c.name,
                            "instrument": c.instrument,
                            "teacher": teacher.name if teacher else "(unknown)",
                            "day": les.get("day"),
                            "start_time": les.get("start_time"),
                            "room": les.get("room"),
                            "students": ", ".join(student_names),
                        }
                    )
        rows.sort(
            key=lambda r: (
                self._parse_time(r.get("start_time")),
                r.get("course_name", ""),
            )
        )
        return rows

    def check_in(self, student_id, course_id):
        """
        Record attendance if the student is enrolled in that course.
        Also logs and persists.
        """
        try:
            sid, cid = int(student_id), int(course_id)
        except (TypeError, ValueError):
            logger.error(
                "Invalid check-in params: student_id=%r course_id=%r",
                student_id,
                course_id,
            )
            return False

        s = self.find_student_by_id(sid)
        c = self.find_course_by_id(cid)
        if not s or not c:
            logger.warning(
                "Check-in rejected: missing student or course (sid=%s cid=%s)",
                sid,
                cid,
            )
            return False

        # Accept if either enrollment linkage exists (robust to partial setup)
        enrolled = (cid in getattr(s, "enrolled_course_ids", [])) or (
            sid in getattr(c, "enrolled_student_ids", [])
        )
        if not enrolled:
            logger.warning(
                "Check-in rejected: sid=%s not enrolled in cid=%s", sid, cid
            )
            return False

        ts = datetime.now().isoformat(timespec="seconds")
        self.attendance_log.append(
            {"student_id": sid, "course_id": cid, "timestamp": ts}
        )
        self._save_data()
        logger.info(
            "Attendance recorded: student %s in course %s at %s", sid, cid, ts
        )
        return ts

    def cancel_lesson(self, lesson_id, reason: str) -> bool:
        """
        Mark a lesson as cancelled and record the reason.
        """
        for course in self.courses:
            for lesson in getattr(course, "lessons", []):
                if str(lesson.get("lesson_id")) == str(lesson_id):
                    lesson["cancelled"] = True
                    lesson["cancel_reason"] = reason
                    self._save_data()
                    logger.warning(
                        "Lesson ID %s cancelled. Reason: %s",
                        lesson_id,
                        reason,
                    )
                    return True
        logger.error("Cancel failed: lesson %s not found", lesson_id)
        return False

    # ---------- Finance ----------
    @classmethod
    def _normalize_method(cls, method: str | None) -> str | None:
        """
        Clean and normalize user-entered payment method (casefold + synonyms)
        so we only store known canonical forms.
        """
        if not method:
            return None
        # collapse whitespace & lowercase
        key = re.sub(r"\s+", " ", str(method)).strip().lower()
        return cls.METHOD_ALIASES.get(key)

    def record_payment(self, student_id, amount, method: str) -> bool:
        """
        Append a finance event: who paid, how much, how, when.
        Validate:
        - student exists
        - amount is positive Decimal
        - method is one of ACCEPTED_METHODS (after normalization)
        """
        # Validate student
        try:
            sid = int(student_id)
        except (TypeError, ValueError):
            logger.error("Failed payment: invalid student_id %r", student_id)
            return False

        student = self.find_student_by_id(sid)
        if not student:
            logger.error("Failed payment: student %s not found.", sid)
            return False

        # Normalize/validate method (case-insensitive + synonyms)
        norm_method = self._normalize_method(method)
        if norm_method not in self.ACCEPTED_METHODS:
            logger.error("Failed payment: unsupported method %r", method)
            return False

        # Validate amount as positive Decimal
        try:
            amt = Decimal(str(amount))
            if amt <= 0:
                raise InvalidOperation
        except (InvalidOperation, ValueError):
            logger.error("Failed payment: invalid amount %r", amount)
            return False

        payment_record = {
            "student_id": sid,                     # normalized int
            # store string to preserve precision
            "amount": str(amt),
            "method": norm_method,                 # store normalized method
            "timestamp": datetime.now().isoformat(timespec="seconds"),
        }
        self.finance_log.append(payment_record)
        self._save_data()
        logger.info(
            "Payment of %s recorded for student ID %s via %s.",
            amt,
            sid,
            norm_method,
        )
        return True

    def get_payment_history(self, student_id) -> list[dict]:
        """
        Return list of payment dicts for a given student.
        """
        try:
            sid = int(student_id)
        except (TypeError, ValueError):
            return []
        out = []
        for p in self.finance_log:
            try:
                if int(p.get("student_id", -1)) == sid:
                    out.append(p)
            except (TypeError, ValueError):
                continue
        return out

    # ---------- Reports / CSV Export ----------
    @staticmethod
    def _mitigate_csv_injection(value: str) -> str:
        """
        Minimal CSV formula injection mitigation: prefix formula-looking cells.
        """
        if isinstance(value, str) and value[:1] in ("=", "+", "-", "@"):
            return "'" + value
        return value

    def export_report(self, kind: str, out_path: str) -> bool:
        """
        Export either "finance" or "attendance" data to CSV.
        """
        if kind == "finance":
            data_to_export = self.finance_log
            headers = ["student_id", "amount", "method", "timestamp"]
        elif kind == "attendance":
            data_to_export = self.attendance_log
            headers = ["student_id", "course_id", "timestamp"]
        else:
            logger.error("Unknown report type: %s", kind)
            return False

        try:
            os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
            with open(out_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=headers)
                writer.writeheader()
                for row in data_to_export:
                    safe_row = {
                        k: self._mitigate_csv_injection(str(row.get(k, "")))
                        for k in headers
                    }
                    writer.writerow(safe_row)
            logger.info("%s report exported to %s.",
                        kind.capitalize(), out_path)
            return True
        except Exception:
            logger.exception(
                "Failed to export %s report to %s", kind, out_path
            )
            return False

    # ---------- Search & Summary / Analytics ----------
    def search_students(self, query: str) -> list[dict]:
        """
        Case-insensitive substring match on student name.
        Returns lightweight dicts for UI tables.
        """
        q = (query or "").lower().strip()
        return [
            {
                "id": s.id,
                "name": s.name,
                "enrolled": len(s.enrolled_course_ids),
                "preferred_instrument": getattr(s, "preferred_instrument", "-"),
            }
            for s in self.students
            if not q or q in s.name.lower()
        ]

    def instrument_summary(self) -> list[dict]:
        """
        Combine: how many students prefer each instrument,
        how many courses exist for that instrument,
        and how many unique students are enrolled.
        """
        pref_counts: dict[str, int] = {}
        enrol_sets: dict[str, set[int]] = {}
        course_counts: dict[str, int] = {}

        for s in self.students:
            instr = getattr(s, "preferred_instrument", None)
            if instr:
                pref_counts[instr] = pref_counts.get(instr, 0) + 1

        for c in self.courses:
            course_counts[c.instrument] = course_counts.get(
                c.instrument, 0) + 1
            enrol_sets.setdefault(c.instrument, set()).update(
                c.enrolled_student_ids
            )

        rows = []
        all_instrs = set(pref_counts) | set(enrol_sets) | set(course_counts)
        for instr in sorted(all_instrs):
            rows.append(
                {
                    "instrument": instr,
                    "registered_students": pref_counts.get(instr, 0),
                    "enrolled_students": len(enrol_sets.get(instr, set())),
                    "courses": course_counts.get(instr, 0),
                }
            )
        rows.sort(
            key=lambda r: (
                -r["registered_students"],
                -r["enrolled_students"],
                r["instrument"],
            )
        )
        return rows

    def attendance_csv(self) -> str:
        """
        Return attendance log as CSV text (string),
        including student/course names for readability.
        """
        # Cache lookups
        id_to_student = {s.id: s.name for s in self.students}
        id_to_course = {c.id: c.name for c in self.courses}

        lines = ["student_id,student_name,course_id,course_name,timestamp"]
        for rec in self.attendance_log:
            sid = rec.get("student_id")
            cid = rec.get("course_id")

            # Mitigate CSV formula injection for free-text fields
            student = self._mitigate_csv_injection(id_to_student.get(sid, ""))
            course = self._mitigate_csv_injection(id_to_course.get(cid, ""))
            ts = self._mitigate_csv_injection(rec.get("timestamp", ""))

            lines.append(
                f"{sid},{student},{cid},{course},{ts}"
            )
        return "\n".join(lines)

    def available_instruments(self) -> list[str]:
        """
        Return all instruments that currently have at least one course.
        """
        return sorted({c.instrument for c in self.courses})

    # ---------- Validation helpers (admin / CRUD support) ----------
    def _is_valid_time(self, hhmm: str) -> bool:
        """
        Validate 24h time format 'HH:MM'.
        """
        return bool(
            re.match(r"^(?:[01]\d|2[0-3]):[0-5]\d$", (hhmm or "").strip())
        )

    def _teacher_name_exists(self, name: str) -> bool:
        """
        Prevent duplicate teacher names.
        """
        n = (name or "").strip().casefold()
        return any(t.name.casefold() == n for t in self.teachers)

    def _course_name_exists(self, name: str) -> bool:
        """
        Prevent duplicate course names.
        """
        n = (name or "").strip().casefold()
        return any(c.name.casefold() == n for c in self.courses)

    def _teacher_slot_taken(self, teacher_id: int, day: str, start_time: str) -> bool:
        """
        Check if a teacher already teaches at that day+time.
        Helps prevent double-booking.
        """
        day = (day or "").strip().lower()
        st = (start_time or "").strip()
        for c in self.courses:
            if c.teacher_id == int(teacher_id):
                for les in getattr(c, "lessons", []):
                    if (
                        (les.get("day", "") or "").strip().lower() == day
                        and (les.get("start_time", "") or "").strip() == st
                    ):
                        return True
        return False

    # ---------- Admin helpers ----------
    def _next_teacher_id(self) -> int:
        return max((t.id for t in self.teachers), default=0) + 1

    def _next_course_id(self) -> int:
        return max((c.id for c in self.courses), default=0) + 1

    def add_teacher(self, name: str, speciality: str):
        """
        Create a new teacher profile and save.
        Returns the new teacher ID, or None on invalid input.
        """
        name = (name or "").strip()
        speciality = (speciality or "").strip()
        if not name or not speciality:
            logger.warning("add_teacher rejected: empty name/speciality.")
            return None
        if self._teacher_name_exists(name):
            logger.warning(
                "add_teacher rejected: duplicate teacher name %r.", name
            )
            return None

        tid = self._next_teacher_id()
        self.teachers.append(TeacherUser(tid, name, speciality))
        self._save_data()
        logger.info(
            "Teacher added: %s (ID %s, speciality %s)",
            name,
            tid,
            speciality,
        )
        return tid

    def add_course(
        self,
        name: str,
        instrument: str,
        teacher_id: int,
        day: str,
        start_time: str,
        room: str,
    ):
        """
        Create a new course/lesson slot.
        Returns the new course ID, or None on invalid input.
        """
        name = (name or "").strip()
        instrument = (instrument or "").strip()
        day = (day or "").strip()
        start_time = (start_time or "").strip()
        room = (room or "").strip()

        teacher = self.find_teacher_by_id(teacher_id)
        if not (name and instrument and teacher and day and start_time and room):
            logger.warning("add_course rejected: missing/invalid fields.")
            return None

        if self._course_name_exists(name):
            logger.warning(
                "add_course rejected: duplicate course name %r.", name
            )
            return None

        if not self._is_valid_time(start_time):
            logger.warning(
                "add_course rejected: invalid time %r.", start_time
            )
            return None

        if self._teacher_slot_taken(teacher.id, day, start_time):
            logger.warning(
                "add_course rejected: teacher %s already teaching %s at %s.",
                teacher.id,
                day,
                start_time,
            )
            return None

        cid = self._next_course_id()
        self.courses.append(
            Course(
                cid,
                name,
                instrument,
                teacher.id,
                enrolled_student_ids=[],
                lessons=[
                    {
                        "lesson_id": self.next_lesson_id,
                        "day": day,
                        "start_time": start_time,
                        "room": room,
                    }
                ],
            )
        )
        self.next_lesson_id += 1
        self._save_data()
        logger.info(
            "Course added: %s (ID %s) for instrument %s with teacher %s.",
            name,
            cid,
            instrument,
            teacher.id,
        )
        return cid

    def enrol_student_to_course(self, student_id: int, course_id: int) -> bool:
        """
        Add a student into a course roster.
        """
        s = self.find_student_by_id(student_id)
        c = self.find_course_by_id(course_id)
        if not s or not c:
            logger.warning(
                "enrol_student_to_course failed: sid=%r cid=%r not found.",
                student_id,
                course_id,
            )
            return False

        # If already enrolled, treat as success (idempotent)
        if c.id in getattr(s, "enrolled_course_ids", []):
            return True

        s.enrolled_course_ids.append(c.id)
        c.enrolled_student_ids.append(s.id)
        self._save_data()
        logger.info("Student %s enrolled to course %s.", s.id, c.id)
        return True

    # ---------- CRUD: Students ----------
    def edit_student(
        self,
        student_id: int,
        name: str | None = None,
        preferred_instrument: str | None = None,
    ) -> bool:
        """
        Update a student's name / preferred instrument.
        """
        s = self.find_student_by_id(student_id)
        if not s:
            return False

        if name is not None:
            nm = name.strip()
            if nm:
                s.name = nm

        if preferred_instrument is not None:
            pi = preferred_instrument.strip()
            s.preferred_instrument = pi if pi else None

        self._save_data()
        logger.info("Student %s edited.", student_id)
        return True

    def delete_student(self, student_id: int) -> bool:
        """
        Fully remove a student:
         - unenrol from courses
         - delete attendance records
         - remove from master list
        """
        s = self.find_student_by_id(student_id)
        if not s:
            return False

        # Remove from each course's roster
        for c in self.courses:
            if s.id in c.enrolled_student_ids:
                c.enrolled_student_ids = [
                    sid for sid in c.enrolled_student_ids if sid != s.id
                ]

        # Remove from attendance log
        self.attendance_log = [
            r for r in self.attendance_log if r.get("student_id") != s.id
        ]

        # Remove from students list
        self.students = [x for x in self.students if x.id != s.id]

        self._save_data()
        logger.warning("Student %s deleted.", student_id)
        return True

    # ---------- CRUD: Courses ----------
    def edit_course(
        self,
        course_id: int,
        name: str | None = None,
        instrument: str | None = None,
        teacher_id: int | None = None,
        day: str | None = None,
        start_time: str | None = None,
        room: str | None = None,
    ) -> bool:
        """
        Update course info (name, teacher, schedule).
        Performs collision checks so we don't double-book teachers.
        """
        c = self.find_course_by_id(course_id)
        if not c:
            return False

        # Validate name uniqueness if changing
        if name is not None:
            new_name = (name or "").strip()
            if not new_name:
                return False
            # can't collide with a different existing course
            if (
                new_name.casefold() != c.name.casefold()
                and any(
                    new_name.casefold() == x.name.casefold()
                    for x in self.courses
                )
            ):
                return False

        # Validate teacher if changing
        new_teacher = None
        if teacher_id is not None:
            new_teacher = self.find_teacher_by_id(int(teacher_id))
            if not new_teacher:
                return False

        # Validate time if changing
        if start_time is not None and start_time.strip():
            if not self._is_valid_time(start_time):
                return False

        # We'll maybe check for teacher booking clashes
        new_day = (
            day
            if day is not None
            else (c.lessons[0].get("day") if getattr(c, "lessons", []) else None)
        )
        new_time = (
            start_time
            if start_time is not None
            else (
                c.lessons[0].get("start_time")
                if getattr(c, "lessons", [])
                else None
            )
        )
        tid = new_teacher.id if new_teacher else c.teacher_id

        if new_day and new_time:
            # Only check if any of (teacher/day/time) actually changes
            if (
                (tid != c.teacher_id)
                or (
                    new_day
                    != (
                        c.lessons[0].get("day")
                        if getattr(c, "lessons", [])
                        else None
                    )
                )
                or (
                    new_time
                    != (
                        c.lessons[0].get("start_time")
                        if getattr(c, "lessons", [])
                        else None
                    )
                )
            ):
                if self._teacher_slot_taken(tid, new_day, new_time):
                    return False

        # Apply edits
        if name is not None:
            c.name = (name or "").strip()
        if instrument is not None:
            c.instrument = (instrument or "").strip()
        if new_teacher is not None:
            c.teacher_id = new_teacher.id

        # Update lesson details
        if (day is not None) or (start_time is not None) or (room is not None):
            if not getattr(c, "lessons", []):
                c.lessons = [
                    {
                        "lesson_id": self.next_lesson_id,
                        "day": "Monday",
                        "start_time": "09:00",
                        "room": "Room A",
                    }
                ]
                self.next_lesson_id += 1
            if day is not None:
                c.lessons[0]["day"] = (day or "").strip()
            if start_time is not None:
                c.lessons[0]["start_time"] = (start_time or "").strip()
            if room is not None:
                c.lessons[0]["room"] = (room or "").strip()

        self._save_data()
        logger.info("Course %s edited.", course_id)
        return True

    def delete_course(self, course_id: int) -> bool:
        """
        Remove a course:
         - unenrol all students from it
         - remove attendance entries for it
         - drop it from course list
        """
        c = self.find_course_by_id(course_id)
        if not c:
            return False

        # Unenrol students from this course
        for s in self.students:
            if c.id in getattr(s, "enrolled_course_ids", []):
                s.enrolled_course_ids = [
                    cid for cid in s.enrolled_course_ids if cid != c.id
                ]

        # Remove attendance for this course
        self.attendance_log = [
            r for r in self.attendance_log if r.get("course_id") != c.id
        ]

        # Remove from courses list
        self.courses = [x for x in self.courses if x.id != c.id]

        self._save_data()
        logger.warning("Course %s deleted.", course_id)
        return True

    # ---------- CRUD: Teachers ----------
    def edit_teacher(
        self,
        teacher_id: int,
        name: str | None = None,
        speciality: str | None = None,
    ) -> bool:
        """
        Update teacher info.
        Enforces unique teacher names.
        """
        t = self.find_teacher_by_id(teacher_id)
        if not t:
            return False

        if name is not None:
            new_name = (name or "").strip()
            if not new_name:
                return False
            # must not collide with another teacher's name
            if (
                new_name.casefold() != t.name.casefold()
                and any(
                    new_name.casefold() == x.name.casefold()
                    for x in self.teachers
                )
            ):
                return False
            t.name = new_name

        if speciality is not None:
            t.speciality = (speciality or "").strip()

        self._save_data()
        logger.info("Teacher %s edited.", teacher_id)
        return True

    def delete_teacher(self, teacher_id: int) -> bool:
        """
        Delete a teacher if they're not currently assigned to any course.
        """
        t = self.find_teacher_by_id(teacher_id)
        if not t:
            return False

        # Can't delete if they're still assigned to any course
        if any(c.teacher_id == t.id for c in self.courses):
            logger.warning(
                "delete_teacher refused: teacher %s still has courses.",
                teacher_id,
            )
            return False

        self.teachers = [x for x in self.teachers if x.id != t.id]
        self._save_data()
        logger.warning("Teacher %s deleted.", teacher_id)
        return True

    def reassign_course_teacher(self, course_id: int, new_teacher_id: int) -> bool:
        """
        Change which teacher teaches a given course,
        but avoid double-booking conflicts.
        """
        c = self.find_course_by_id(course_id)
        new_t = self.find_teacher_by_id(new_teacher_id)
        if not c or not new_t:
            return False

        # avoid double booking for the time slot
        if getattr(c, "lessons", []):
            day = c.lessons[0].get("day", "")
            stime = c.lessons[0].get("start_time", "")
            if self._teacher_slot_taken(new_t.id, day, stime):
                return False

        c.teacher_id = new_t.id
        self._save_data()
        logger.info(
            "Teacher for course %s reassigned to %s.",
            course_id,
            new_teacher_id,
        )
        return True
