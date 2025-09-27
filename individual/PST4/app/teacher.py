from .user import User


class TeacherUser(User):
    def __init__(self, user_id: int, name: str, speciality: str):
        super().__init__(user_id, name)
        self.speciality = speciality

    def to_dict(self) -> dict:
        return {"id": self.id, "name": self.name, "speciality": self.speciality}

    @staticmethod
    def from_dict(d: dict) -> "TeacherUser":
        return TeacherUser(d["id"], d["name"], d["speciality"])


class Course:
    def __init__(self, course_id: int, name: str, instrument: str, teacher_id: int,
                 enrolled_student_ids=None, lessons=None):
        self.id = course_id
        self.name = name
        self.instrument = instrument
        self.teacher_id = teacher_id
        self.enrolled_student_ids = list(enrolled_student_ids or [])
        # [{lesson_id, day, start_time, room}]
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
    def from_dict(d: dict) -> "Course":
        return Course(
            d["id"], d["name"], d["instrument"], d["teacher_id"],
            d.get("enrolled_student_ids", []), d.get("lessons", [])
        )
