"""
App package for the Music School Management System (MSMS).
Exposes the main classes so they can be imported directly from app.
"""

from .user import User
from .student import StudentUser
from .teacher import TeacherUser, Course
from .schedule import ScheduleManager

__all__ = ["User", "StudentUser", "TeacherUser", "Course", "ScheduleManager"]
