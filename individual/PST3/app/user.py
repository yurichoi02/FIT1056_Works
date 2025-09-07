# app/user.py
class User:
    def __init__(self, uid: int, name: str):
        self.id = uid
        self.name = name

    def to_dict(self) -> dict:
        return {"id": self.id, "name": self.name}

    @staticmethod
    def from_dict(d: dict):
        # base isn't used directly, but keeping for completeness
        return User(d["id"], d["name"])
