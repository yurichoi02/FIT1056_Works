# app/teacher.py
from .user import User


class TeacherUser(User):
    def __init__(self, uid: int, name: str, speciality: str):
        super().__init__(uid, name)
        self.speciality = (speciality or "").strip().title()

    def to_dict(self) -> dict:
        base = super().to_dict()
        base["speciality"] = self.speciality
        return base

    @staticmethod
    def from_dict(d: dict):
        return TeacherUser(
            uid=d["id"],
            name=d["name"],
            speciality=d.get("speciality", ""),
        )


class Course:
    def __init__(self, cid: int, name: str, instrument: str, teacher_id: int,
                 enrolled_student_ids=None, lessons=None):
        self.id = cid
        self.name = name.strip()
        self.instrument = (instrument or "").strip().title()
        self.teacher_id = teacher_id
        self.enrolled_student_ids = list(enrolled_student_ids or [])
        # lessons are dicts: {"lesson_id", "day", "start_time", "room"}
        self.lessons = list(lessons or [])

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "instrument": self.instrument,
            "teacher_id": self.teacher_id,
            "enrolled_student_ids": list(self.enrolled_student_ids),
            "lessons": list(self.lessons),
        }

    @staticmethod
    def from_dict(d: dict):
        return Course(
            cid=d["id"],
            name=d["name"],
            instrument=d["instrument"],
            teacher_id=d["teacher_id"],
            enrolled_student_ids=d.get("enrolled_student_ids", []),
            lessons=d.get("lessons", []),
        )
