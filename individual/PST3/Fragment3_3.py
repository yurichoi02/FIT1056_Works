# Fragment3_3.py
# Check-in method for ScheduleManager (PST3, Fragment 3.3)
# This is the snippet I added inside ScheduleManager in app/schedule.py

import datetime


def check_in(self, student_id: int, course_id: int):
    """Record a student's attendance for a course after validation."""
    student = self.find_student_by_id(student_id)
    course = self.find_course_by_id(course_id)

    if not student:
        raise ValueError(f"No student with ID {student_id}")
    if not course:
        raise ValueError(f"No course with ID {course_id}")
    if course_id not in student.enrolled_course_ids:
        raise ValueError(
            f"Student {student.name} is not enrolled in {course.name}")

    ts = datetime.datetime.now().isoformat(timespec="seconds")
    record = {"student_id": student_id,
              "course_id": course_id, "timestamp": ts}
    self.attendance_log.append(record)
    self._save_data()
    return ts

# note: requires find_student_by_id and find_course_by_id helpers
