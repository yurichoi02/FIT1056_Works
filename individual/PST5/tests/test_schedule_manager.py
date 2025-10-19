# tests/test_schedule_manager.py
import pytest
from app.schedule import ScheduleManager
from app.student import StudentUser
from app.teacher import TeacherUser, Course


@pytest.fixture
def fresh_manager(tmp_path):
    """Fresh manager with an isolated temp data file per test."""
    test_file = tmp_path / "test_data.json"
    return ScheduleManager(data_path=str(test_file))


def test_add_course_and_cancel_lesson(fresh_manager):
    """Cancelling a lesson updates data and returns True."""
    # Arrange
    teacher = TeacherUser(1, "Mr. Smith", "Piano")
    course = Course(
        1, "Beginner Piano", "Piano", teacher_id=1,
        enrolled_student_ids=[],
        lessons=[{"lesson_id": 10, "day": "Monday",
                  "start_time": "10:00", "room": "Room 1"}]
    )
    fresh_manager.teachers.append(teacher)
    fresh_manager.courses.append(course)

    # Act
    result = fresh_manager.cancel_lesson(10, "Teacher unavailable")

    # Assert
    assert result is True
    lesson = fresh_manager.courses[0].lessons[0]
    assert lesson.get("cancelled") is True
    assert "Teacher unavailable" in lesson.get("cancel_reason", "")


def test_record_payment_and_history(fresh_manager):
    """Payments are recorded and retrievable for a specific student."""
    # Arrange
    student = StudentUser(1, "Alice", [], "Piano")
    fresh_manager.students.append(student)

    # Act (manager accepts synonyms like "Credit Card" and normalizes to "card")
    ok = fresh_manager.record_payment(1, "100.00", "Credit Card")
    assert ok is True
    history = fresh_manager.get_payment_history(1)

    # Assert
    assert len(history) == 1
    assert history[0]["amount"] == "100.00"     # stored as string
    assert history[0]["method"] == "card"       # normalized
    assert str(history[0]["student_id"]) == "1"


def test_get_payment_history_no_results(fresh_manager):
    """Unknown student returns an empty history list."""
    # Act
    result = fresh_manager.get_payment_history(999)
    # Assert
    assert result == []


def test_export_report_creates_finance_csv(fresh_manager, tmp_path):
    """Finance CSV export creates a file with expected headers/content."""
    # Arrange
    student = StudentUser(1, "Bob", [], "Guitar")
    fresh_manager.students.append(student)
    assert fresh_manager.record_payment(
        1, "150.00", "Cash") is True  # normalized to "cash"
    out = tmp_path / "finance_report.csv"

    # Act
    ok = fresh_manager.export_report("finance", str(out))

    # Assert
    assert ok is True
    assert out.exists()
    text = out.read_text(encoding="utf-8")
    assert "student_id" in text and "amount" in text and "method" in text


def test_export_attendance_report_creates_file(fresh_manager, tmp_path):
    """Attendance CSV export creates a file and includes correct header."""
    # Arrange: minimal student/course to allow check_in
    s = StudentUser(1, "Cara", [], "Violin")
    t = TeacherUser(1, "Ms. Lee", "Violin")
    c = Course(
        1, "Beginner Violin", "Violin", teacher_id=1,
        enrolled_student_ids=[1],
        lessons=[{"lesson_id": 7, "day": "Monday",
                  "start_time": "09:00", "room": "A1"}]
    )
    fresh_manager.students.append(s)
    fresh_manager.teachers.append(t)
    fresh_manager.courses.append(c)

    # Act: check in then export attendance
    ts = fresh_manager.check_in(1, 1)
    assert isinstance(ts, str) and len(ts) > 0  # timestamp string
    out = tmp_path / "attendance.csv"
    ok = fresh_manager.export_report("attendance", str(out))

    # Assert
    assert ok is True
    assert out.exists()
    text = out.read_text(encoding="utf-8")
    assert "student_id,course_id,timestamp" in text


def test_export_report_invalid_kind_returns_false(fresh_manager, tmp_path):
    """Invalid report kind is handled safely."""
    # Act
    ok = fresh_manager.export_report("bad_kind", str(tmp_path / "x.csv"))
    # Assert
    assert ok is False
