from .user import User


class StudentUser(User):
    def __init__(self, user_id: int, name: str, enrolled_course_ids=None, preferred_instrument=None):
        super().__init__(user_id, name)
        self.enrolled_course_ids = list(enrolled_course_ids or [])
        self.preferred_instrument = preferred_instrument
        self.registered_at = None

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "enrolled_course_ids": list(self.enrolled_course_ids),
            "registered_at": getattr(self, "registered_at", None),
            "preferred_instrument": getattr(self, "preferred_instrument", None)
        }

    @staticmethod
    def from_dict(d: dict) -> "StudentUser":
        obj = StudentUser(d["id"], d["name"], d.get(
            "enrolled_course_ids", []), d.get("preferred_instrument"))
        if "registered_at" in d:
            obj.registered_at = d["registered_at"]
        return obj
