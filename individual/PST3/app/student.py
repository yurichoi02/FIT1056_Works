# app/student.py
from .user import User


class StudentUser(User):
    def __init__(self, uid: int, name: str, enrolled_course_ids=None):
        super().__init__(uid, name)
        self.enrolled_course_ids = list(enrolled_course_ids or [])

    def to_dict(self) -> dict:
        base = super().to_dict()
        base["enrolled_course_ids"] = list(self.enrolled_course_ids)
        return base

    @staticmethod
    def from_dict(d: dict):
        return StudentUser(
            uid=d["id"],
            name=d["name"],
            enrolled_course_ids=d.get("enrolled_course_ids", []),
        )
