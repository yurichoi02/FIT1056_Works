# app/schedule.py
import json
import os
import datetime
from .student import StudentUser
from .teacher import TeacherUser, Course


class ScheduleManager:
    def __init__(self, data_path="data/msms.json"):
        self.data_path = data_path
        self.students: list[StudentUser] = []
        self.teachers: list[TeacherUser] = []
        self.courses: list[Course] = []
        self.attendance_log: list[dict] = []  # PST3 Fragment 3.2
        # simple counters (recomputed on load)
        self._next_student_id = 1
        self._next_teacher_id = 1
        self._next_course_id = 1
        self._load_data()

    # ---------- persistence ----------
    def _load_data(self):
        if not os.path.exists(self.data_path):
            return
        with open(self.data_path, "r", encoding="utf-8") as f:
            raw = json.load(f)

        self.students = [StudentUser.from_dict(
            d) for d in raw.get("students", [])]
        self.teachers = [TeacherUser.from_dict(
            d) for d in raw.get("teachers", [])]
        self.courses = [Course.from_dict(d) for d in raw.get("courses", [])]
        self.attendance_log = list(raw.get("attendance", []))

        self._next_student_id = max(
            (s.id for s in self.students), default=0) + 1
        self._next_teacher_id = max(
            (t.id for t in self.teachers), default=0) + 1
        self._next_course_id = max((c.id for c in self.courses), default=0) + 1

    def _save_data(self):
        data = {
            "students": [s.to_dict() for s in self.students],
            "teachers": [t.to_dict() for t in self.teachers],
            "courses":  [c.to_dict() for c in self.courses],
            "attendance": list(self.attendance_log),
        }
        os.makedirs(os.path.dirname(self.data_path), exist_ok=True)
        with open(self.data_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    # ---------- finders ----------
    def find_student_by_id(self, sid: int) -> StudentUser | None:
        return next((s for s in self.students if s.id == sid), None)

    def find_teacher_by_id(self, tid: int) -> TeacherUser | None:
        return next((t for t in self.teachers if t.id == tid), None)

    def find_course_by_id(self, cid: int) -> Course | None:
        return next((c for c in self.courses if c.id == cid), None)

    # ---------- OOP versions of PST2 operations ----------
    def add_student(self, name: str) -> StudentUser:
        s = StudentUser(self._next_student_id, name.strip(), [])
        self._next_student_id += 1
        self.students.append(s)
        self._save_data()
        return s

    def add_teacher(self, name: str, speciality: str) -> TeacherUser:
        t = TeacherUser(self._next_teacher_id, name.strip(), speciality)
        self._next_teacher_id += 1
        self.teachers.append(t)
        self._save_data()
        return t

    def add_course(self, name: str, instrument: str, teacher_id: int) -> Course:
        if not self.find_teacher_by_id(teacher_id):
            raise ValueError(f"No teacher with ID {teacher_id}")
        c = Course(self._next_course_id, name.strip(), instrument, teacher_id)
        self._next_course_id += 1
        self.courses.append(c)
        self._save_data()
        return c

    def enrol_student_to_course(self, student_id: int, course_id: int):
        s = self.find_student_by_id(student_id)
        c = self.find_course_by_id(course_id)
        if not s:
            raise ValueError(f"No student with ID {student_id}")
        if not c:
            raise ValueError(f"No course with ID {course_id}")
        if course_id not in s.enrolled_course_ids:
            s.enrolled_course_ids.append(course_id)
        if student_id not in c.enrolled_student_ids:
            c.enrolled_student_ids.append(student_id)
        self._save_data()

    # ---------- PST2 feature parity ----------
    def reassign_teacher(self, course_id: int, new_teacher_id: int):
        c = self.find_course_by_id(course_id)
        t = self.find_teacher_by_id(new_teacher_id)
        if not c:
            raise ValueError(f"No course with ID {course_id}")
        if not t:
            raise ValueError(f"No teacher with ID {new_teacher_id}")
        if t.speciality.lower() != c.instrument.lower():
            raise ValueError(
                f"Teacher speciality '{t.speciality}' does not match course instrument '{c.instrument}'."
            )
        c.teacher_id = new_teacher_id
        self._save_data()

    def instrument_summary(self) -> dict:
        counts: dict[str, int] = {}
        for c in self.courses:
            counts[c.instrument.lower()] = counts.get(
                c.instrument.lower(), 0) + len(c.enrolled_student_ids)
        return {k.title(): v for k, v in counts.items()}

    def find_students_by_instrument(self, instrument_term: str):
        term = (instrument_term or "").strip().lower()
        matched = {c.id for c in self.courses if term in c.instrument.lower()}
        return [s for s in self.students if any(cid in matched for cid in s.enrolled_course_ids)]

    def view_assignments_for_student(self, student_id: int) -> list[dict]:
        s = self.find_student_by_id(student_id)
        if not s:
            raise ValueError(f"No student with ID {student_id}")
        out = []
        for cid in s.enrolled_course_ids:
            c = self.find_course_by_id(cid)
            if not c:
                continue
            t = self.find_teacher_by_id(c.teacher_id)
            out.append({
                "course_id": c.id,
                "course_name": c.name,
                "instrument": c.instrument,
                "teacher": t.name if t else "(unknown)",
            })
        return out

    # ---------- Fragment 3.3: check-in (strict version) ----------
    def check_in(self, student_id: int, course_id: int):
        s = self.find_student_by_id(student_id)
        c = self.find_course_by_id(course_id)
        if not s:
            raise ValueError(f"No student with ID {student_id}")
        if not c:
            raise ValueError(f"No course with ID {course_id}")
        if course_id not in s.enrolled_course_ids:
            raise ValueError(f"Student {s.name} is not enrolled in {c.name}.")
        ts = datetime.datetime.now().isoformat(timespec="seconds")
        self.attendance_log.append(
            {"student_id": student_id, "course_id": course_id, "timestamp": ts})
        self._save_data()
        return ts

    # ---------- PST3 extras ----------
    def get_daily_roster(self, day: str) -> list[dict]:
        day_norm = (day or "").strip().title()
        roster = []
        for c in self.courses:
            t = self.find_teacher_by_id(c.teacher_id)
            for les in c.lessons:
                if (les.get("day", "").strip().title() == day_norm):
                    roster.append({
                        "course_id": c.id,
                        "course_name": c.name,
                        "instrument": c.instrument,
                        "teacher": t.name if t else "(unknown)",
                        "start_time": les.get("start_time", ""),
                        "room": les.get("room", ""),
                    })
        roster.sort(key=lambda x: (x["start_time"], x["room"]))
        return roster

    def get_student_schedule(self, student_id: int) -> list[dict]:
        s = self.find_student_by_id(student_id)
        if not s:
            raise ValueError(f"No student with ID {student_id}")
        items = []
        for cid in s.enrolled_course_ids:
            c = self.find_course_by_id(cid)
            if not c:
                continue
            t = self.find_teacher_by_id(c.teacher_id)
            if c.lessons:
                for les in c.lessons:
                    items.append({
                        "course_name": c.name,
                        "instrument": c.instrument,
                        "teacher": t.name if t else "(unknown)",
                        "day": les.get("day", ""),
                        "start_time": les.get("start_time", ""),
                        "room": les.get("room", ""),
                    })
            else:
                items.append({
                    "course_name": c.name,
                    "instrument": c.instrument,
                    "teacher": t.name if t else "(unknown)",
                    "day": "(unscheduled)",
                    "start_time": "",
                    "room": "",
                })
        items.sort(key=lambda x: (x["day"], x["start_time"]))
        return items
