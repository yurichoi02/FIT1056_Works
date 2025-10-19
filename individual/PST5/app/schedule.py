# app/schedule.py
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

        # ewallets (MY examples included)
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
                "Data file corrupted or invalid JSON. Starting fresh dataset (backup preserved).")
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

        # Track next lesson id
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

    # ---------- Student Management ----------
    def _next_student_id(self) -> int:
        return max((s.id for s in self.students), default=0) + 1

    def register_new_student(self, name: str, instrument: str):
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
            (c for c in self.courses if c.instrument.lower()
             == instrument.lower()), None
        )
        if match:
            student.enrolled_course_ids.append(match.id)
            match.enrolled_student_ids.append(sid)

        self.students.append(student)
        self._save_data()
        logger.info("New student registered: %s (ID %s)", name, sid)
        return sid

    def list_students(self) -> list[dict]:
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
        try:
            h, m = map(int, (t or "").split(":"))
            return time(h, m)
        except Exception:
            return time.max  # push malformed times to end

    def daily_roster(self, day: str) -> list[dict]:
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
        rows.sort(key=lambda r: (self._parse_time(
            r.get("start_time")), r.get("course_name", "")))
        return rows

    def check_in(self, student_id, course_id):
        try:
            sid, cid = int(student_id), int(course_id)
        except (TypeError, ValueError):
            logger.error(
                "Invalid check-in params: student_id=%r course_id=%r", student_id, course_id)
            return False

        s = self.find_student_by_id(sid)
        c = self.find_course_by_id(cid)
        if not s or not c:
            logger.warning(
                "Check-in rejected: missing student or course (sid=%s cid=%s)", sid, cid)
            return False

        # Accept if either enrollment linkage exists (robust to partial setup in tests/fixtures)
        enrolled = (cid in getattr(s, "enrolled_course_ids", [])) or (
            sid in getattr(c, "enrolled_student_ids", []))
        if not enrolled:
            logger.warning(
                "Check-in rejected: sid=%s not enrolled in cid=%s", sid, cid)
            return False

        ts = datetime.now().isoformat(timespec="seconds")
        self.attendance_log.append(
            {"student_id": sid, "course_id": cid, "timestamp": ts})
        self._save_data()
        logger.info(
            "Attendance recorded: student %s in course %s at %s", sid, cid, ts)
        return ts

    def cancel_lesson(self, lesson_id, reason: str) -> bool:
        """Cancel a lesson by id and record the reason."""
        for course in self.courses:
            for lesson in getattr(course, "lessons", []):
                if str(lesson.get("lesson_id")) == str(lesson_id):
                    lesson["cancelled"] = True
                    lesson["cancel_reason"] = reason
                    self._save_data()
                    logger.warning(
                        "Lesson ID %s cancelled. Reason: %s", lesson_id, reason)
                    return True
        logger.error("Cancel failed: lesson %s not found", lesson_id)
        return False

    # ---------- Finance ----------
    @classmethod
    def _normalize_method(cls, method: str | None) -> str | None:
        if not method:
            return None
        # collapse whitespace & lowercase
        key = re.sub(r"\s+", " ", str(method)).strip().lower()
        return cls.METHOD_ALIASES.get(key)

    def record_payment(self, student_id, amount, method: str) -> bool:
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
        logger.info("Payment of %s recorded for student ID %s via %s.",
                    amt, sid, norm_method)
        return True

    def get_payment_history(self, student_id) -> list[dict]:
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

    # ---------- Reports ----------
    @staticmethod
    def _mitigate_csv_injection(value: str) -> str:
        # Minimal protection for Excel CSV formula injection
        if isinstance(value, str) and value[:1] in ("=", "+", "-", "@"):
            return "'" + value
        return value

    def export_report(self, kind: str, out_path: str) -> bool:
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
                    safe_row = {k: self._mitigate_csv_injection(
                        str(row.get(k, ""))) for k in headers}
                    writer.writerow(safe_row)
            logger.info("%s report exported to %s.",
                        kind.capitalize(), out_path)
            return True
        except Exception:
            logger.exception(
                "Failed to export %s report to %s", kind, out_path)
            return False

    # ---------- Search & Summary ----------
    def search_students(self, query: str) -> list[dict]:
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
                c.enrolled_student_ids)

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
            key=lambda r: (-r["registered_students"], -
                           r["enrolled_students"], r["instrument"])
        )
        return rows

    def attendance_csv(self) -> str:
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
            lines.append(f"{sid},{student},{cid},{course},{ts}")
        return "\n".join(lines)

    def available_instruments(self) -> list[str]:
        return sorted({c.instrument for c in self.courses})
