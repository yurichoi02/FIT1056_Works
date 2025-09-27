import json
import re
from datetime import datetime
from app.student import StudentUser
from app.teacher import TeacherUser, Course


class ScheduleManager:
    def __init__(self, data_path="data/msms.json"):
        self.data_path = data_path
        self.students = []
        self.teachers = []
        self.courses = []
        self.attendance_log = []
        self.next_lesson_id = 1
        self._load_data()

    # ---------- Persistence ----------
    def _load_data(self):
        try:
            with open(self.data_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            self.students = [StudentUser.from_dict(
                d) for d in data.get('students', [])]
            self.teachers = [TeacherUser.from_dict(
                d) for d in data.get('teachers', [])]
            self.courses = [Course.from_dict(d)
                            for d in data.get('courses', [])]
            self.attendance_log = list(data.get('attendance', []))
            max_id = 0
            for c in self.courses:
                for les in c.lessons:
                    try:
                        max_id = max(max_id, int(les.get("lesson_id", 0)))
                    except Exception:
                        pass
            self.next_lesson_id = max_id + 1
        except FileNotFoundError:
            print("Data file not found. Starting clean.")
            self.students, self.teachers, self.courses = [], [], []
            self.attendance_log = []

    def _save_data(self):
        data_to_save = {
            'students': [s.to_dict() for s in self.students],
            'teachers': [t.to_dict() for t in self.teachers],
            'courses':  [c.to_dict() for c in self.courses],
            'attendance': list(self.attendance_log),
        }
        with open(self.data_path, 'w', encoding='utf-8') as f:
            json.dump(data_to_save, f, indent=2)

    # ---------- Finders ----------
    def find_student_by_id(self, sid): return next(
        (s for s in self.students if s.id == sid), None)

    def find_teacher_by_id(self, tid): return next(
        (t for t in self.teachers if t.id == tid), None)

    def find_course_by_id(self, cid): return next(
        (c for c in self.courses if c.id == cid), None)

    # ---------- Student Management ----------
    def _next_student_id(self): return max(
        (s.id for s in self.students), default=0) + 1

    def register_new_student(self, name, instrument):
        name, instrument = (name or '').strip(), (instrument or '').strip()
        if not name or not instrument:
            return None
        sid = self._next_student_id()
        student = StudentUser(sid, name, enrolled_course_ids=[
        ], preferred_instrument=instrument)
        student.registered_at = datetime.now().isoformat(timespec="seconds")
        match = next(
            (c for c in self.courses if c.instrument.lower() == instrument.lower()), None)
        if match:
            student.enrolled_course_ids.append(match.id)
            match.enrolled_student_ids.append(sid)
        self.students.append(student)
        self._save_data()
        return sid

    def list_students(self):
        return [{
            "id": s.id, "name": s.name, "enrolled": len(s.enrolled_course_ids),
            "registered_at": getattr(s, "registered_at", "N/A"),
            "preferred_instrument": getattr(s, "preferred_instrument", "-")
        } for s in self.students]

    # ---------- Roster & Attendance ----------
    def daily_roster(self, day: str):
        rows = []
        for c in self.courses:
            teacher = self.find_teacher_by_id(c.teacher_id)
            for les in c.lessons:
                if les.get('day', '').lower() == (day or '').lower():
                    student_names = [self.find_student_by_id(sid).name
                                     for sid in c.enrolled_student_ids if self.find_student_by_id(sid)]
                    rows.append({
                        "course_id": c.id, "course_name": c.name, "instrument": c.instrument,
                        "teacher": teacher.name if teacher else "(unknown)",
                        "day": les.get("day"), "start_time": les.get("start_time"),
                        "room": les.get("room"), "students": ", ".join(student_names)
                    })
        rows.sort(key=lambda r: r.get("start_time", "") or "")
        return rows

    def check_in(self, student_id, course_id):
        s, c = self.find_student_by_id(
            int(student_id)), self.find_course_by_id(int(course_id))
        if not s or not c:
            return False
        if c.id not in s.enrolled_course_ids:
            return False
        ts = datetime.now().isoformat(timespec="seconds")
        self.attendance_log.append(
            {"student_id": s.id, "course_id": c.id, "timestamp": ts})
        self._save_data()
        return ts

    # ---------- Extras ----------
    def search_students(self, query: str):
        q = (query or "").lower().strip()
        return [{
            "id": s.id, "name": s.name, "enrolled": len(s.enrolled_course_ids),
            "preferred_instrument": getattr(s, "preferred_instrument", "-")
        } for s in self.students if not q or q in s.name.lower()]

    def instrument_summary(self):
        pref_counts, enrol_counts, course_counts = {}, {}, {}
        for s in self.students:
            instr = getattr(s, "preferred_instrument", None)
            if instr:
                pref_counts[instr] = pref_counts.get(instr, 0) + 1
        for c in self.courses:
            course_counts[c.instrument] = course_counts.get(
                c.instrument, 0) + 1
            enrol_counts.setdefault(c.instrument, set()).update(
                c.enrolled_student_ids)
        rows, all_instrs = [], set(pref_counts) | set(
            enrol_counts) | set(course_counts)
        for instr in sorted(all_instrs):
            rows.append({
                "instrument": instr,
                "registered_students": pref_counts.get(instr, 0),
                "enrolled_students": len(enrol_counts.get(instr, set())),
                "courses": course_counts.get(instr, 0)
            })
        rows.sort(key=lambda r: (-r["registered_students"], -
                  r["enrolled_students"], r["instrument"]))
        return rows

    def attendance_csv(self):
        lines = ["student_id,student_name,course_id,course_name,timestamp"]
        for rec in self.attendance_log:
            s = self.find_student_by_id(rec.get("student_id"))
            c = self.find_course_by_id(rec.get("course_id"))
            lines.append(
                f"{rec.get('student_id')},{s.name if s else ''},{rec.get('course_id')},{c.name if c else ''},{rec.get('timestamp')}")
        return "\n".join(lines)

    def available_instruments(self):
        return sorted({c.instrument for c in self.courses})

    # ---------- Validation helpers ----------
    def _is_valid_time(self, hhmm: str) -> bool:
        return bool(re.match(r"^(?:[01]\d|2[0-3]):[0-5]\d$", (hhmm or '').strip()))

    def _teacher_name_exists(self, name: str) -> bool:
        n = (name or '').strip().casefold()
        return any(t.name.casefold() == n for t in self.teachers)

    def _course_name_exists(self, name: str) -> bool:
        n = (name or '').strip().casefold()
        return any(c.name.casefold() == n for c in self.courses)

    def _teacher_slot_taken(self, teacher_id: int, day: str, start_time: str) -> bool:
        day = (day or '').strip().lower()
        st = (start_time or '').strip()
        for c in self.courses:
            if c.teacher_id == int(teacher_id):
                for les in c.lessons:
                    if les.get('day', '').lower() == day and les.get('start_time', '') == st:
                        return True
        return False

    # ---------- Admin helpers ----------
    def _next_teacher_id(self):
        return max((t.id for t in self.teachers), default=0) + 1

    def _next_course_id(self):
        return max((c.id for c in self.courses), default=0) + 1

    def add_teacher(self, name: str, speciality: str):
        name = (name or '').strip()
        speciality = (speciality or '').strip()
        if not name or not speciality:
            return None
        if self._teacher_name_exists(name):
            return None
        tid = self._next_teacher_id()
        self.teachers.append(TeacherUser(tid, name, speciality))
        self._save_data()
        return tid

    def add_course(self, name: str, instrument: str, teacher_id: int, day: str, start_time: str, room: str):
        name, instrument, day, start_time, room = (name or '').strip(), (instrument or '').strip(
        ), (day or '').strip(), (start_time or '').strip(), (room or '').strip()
        teacher = self.find_teacher_by_id(
            int(teacher_id)) if teacher_id is not None else None
        if not (name and instrument and teacher and day and start_time and room):
            return None
        if self._course_name_exists(name):
            return None
        if not self._is_valid_time(start_time):
            return None
        if self._teacher_slot_taken(teacher.id, day, start_time):
            return None
        cid = self._next_course_id()
        self.courses.append(Course(cid, name, instrument, teacher.id, enrolled_student_ids=[], lessons=[
            {"lesson_id": self.next_lesson_id, "day": day,
                "start_time": start_time, "room": room}
        ]))
        self.next_lesson_id += 1
        self._save_data()
        return cid

    def enrol_student_to_course(self, student_id: int, course_id: int):
        s, c = self.find_student_by_id(
            int(student_id)), self.find_course_by_id(int(course_id))
        if not s or not c:
            return False
        if c.id in s.enrolled_course_ids:
            return True
        s.enrolled_course_ids.append(c.id)
        c.enrolled_student_ids.append(s.id)
        self._save_data()
        return True

    # ---------- CRUD: Students ----------
    def edit_student(self, student_id: int, name: str | None = None, preferred_instrument: str | None = None) -> bool:
        s = self.find_student_by_id(int(student_id))
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
        return True

    def delete_student(self, student_id: int) -> bool:
        s = self.find_student_by_id(int(student_id))
        if not s:
            return False
        for c in self.courses:
            if s.id in c.enrolled_student_ids:
                c.enrolled_student_ids = [
                    sid for sid in c.enrolled_student_ids if sid != s.id]
        self.attendance_log = [
            r for r in self.attendance_log if r.get("student_id") != s.id]
        self.students = [x for x in self.students if x.id != s.id]
        self._save_data()
        return True

    # ---------- CRUD: Courses ----------
    def edit_course(self, course_id: int, name: str | None = None, instrument: str | None = None,
                    teacher_id: int | None = None, day: str | None = None,
                    start_time: str | None = None, room: str | None = None) -> bool:
        c = self.find_course_by_id(int(course_id))
        if not c:
            return False
        if name is not None:
            new_name = (name or "").strip()
            if not new_name:
                return False
            if new_name.casefold() != c.name.casefold() and any(new_name.casefold() == x.name.casefold() for x in self.courses):
                return False
        new_teacher = None
        if teacher_id is not None:
            new_teacher = self.find_teacher_by_id(int(teacher_id))
            if not new_teacher:
                return False
        if start_time is not None and start_time.strip():
            if not self._is_valid_time(start_time):
                return False
        new_day = day if day is not None else (
            c.lessons[0].get("day") if c.lessons else None)
        new_time = start_time if start_time is not None else (
            c.lessons[0].get("start_time") if c.lessons else None)
        tid = (new_teacher.id if new_teacher else c.teacher_id)
        if new_day and new_time:
            if (tid != c.teacher_id) or (new_day != (c.lessons[0].get("day") if c.lessons else None)) or (new_time != (c.lessons[0].get("start_time") if c.lessons else None)):
                if self._teacher_slot_taken(tid, new_day, new_time):
                    return False
        if name is not None:
            c.name = new_name
        if instrument is not None:
            c.instrument = (instrument or "").strip()
        if new_teacher is not None:
            c.teacher_id = new_teacher.id
        if (day is not None) or (start_time is not None) or (room is not None):
            if not c.lessons:
                c.lessons = [{"lesson_id": self.next_lesson_id,
                              "day": "Monday", "start_time": "09:00", "room": "Room A"}]
                self.next_lesson_id += 1
            if day is not None:
                c.lessons[0]["day"] = (day or "").strip()
            if start_time is not None:
                c.lessons[0]["start_time"] = (start_time or "").strip()
            if room is not None:
                c.lessons[0]["room"] = (room or "").strip()
        self._save_data()
        return True

    def delete_course(self, course_id: int) -> bool:
        c = self.find_course_by_id(int(course_id))
        if not c:
            return False
        for s in self.students:
            if c.id in s.enrolled_course_ids:
                s.enrolled_course_ids = [
                    cid for cid in s.enrolled_course_ids if cid != c.id]
        self.attendance_log = [
            r for r in self.attendance_log if r.get("course_id") != c.id]
        self.courses = [x for x in self.courses if x.id != c.id]
        self._save_data()
        return True

    # ---------- CRUD: Teachers ----------
    def edit_teacher(self, teacher_id: int, name: str | None = None, speciality: str | None = None) -> bool:
        t = self.find_teacher_by_id(int(teacher_id))
        if not t:
            return False
        if name is not None:
            new_name = (name or "").strip()
            if not new_name:
                return False
            if new_name.casefold() != t.name.casefold() and any(new_name.casefold() == x.name.casefold() for x in self.teachers):
                return False
            t.name = new_name
        if speciality is not None:
            t.speciality = (speciality or "").strip()
        self._save_data()
        return True

    def delete_teacher(self, teacher_id: int) -> bool:
        t = self.find_teacher_by_id(int(teacher_id))
        if not t:
            return False
        if any(c.teacher_id == t.id for c in self.courses):
            return False
        self.teachers = [x for x in self.teachers if x.id != t.id]
        self._save_data()
        return True

    def reassign_course_teacher(self, course_id: int, new_teacher_id: int) -> bool:
        c = self.find_course_by_id(int(course_id))
        new_t = self.find_teacher_by_id(int(new_teacher_id))
        if not c or not new_t:
            return False
        if c.lessons:
            day = c.lessons[0].get("day", "")
            stime = c.lessons[0].get("start_time", "")
            if self._teacher_slot_taken(new_t.id, day, stime):
                return False
        c.teacher_id = new_t.id
        self._save_data()
        return True
