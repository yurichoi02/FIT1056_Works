# Fragment2_2.py
# CRUD operations for Teachers and Students

from MSMS import app_data

def add_teacher(name, speciality):
    tid = app_data["next_teacher_id"]
    teacher = {"id": tid, "name": name, "speciality": speciality}
    app_data["teachers"].append(teacher)
    app_data["next_teacher_id"] += 1
    print(f"Teacher '{name}' added.")

def update_teacher(teacher_id, new_name=None, new_speciality=None):
    for t in app_data["teachers"]:
        if t["id"] == teacher_id:
            if new_name:
                t["name"] = new_name
            if new_speciality:
                t["speciality"] = new_speciality
            print(f"Teacher {teacher_id} updated.")
            return
    print("Teacher not found.")

def remove_teacher(teacher_id):
    for t in app_data["teachers"]:
        if t["id"] == teacher_id:
            app_data["teachers"].remove(t)
            print(f"Teacher {teacher_id} removed.")
            return
    print("Teacher not found.")

def add_student(name, instrument):
    sid = app_data["next_student_id"]
    student = {"id": sid, "name": name, "instrument": instrument}
    app_data["students"].append(student)
    app_data["next_student_id"] += 1
    print(f"Student '{name}' added.")

def update_student(student_id, new_name=None, new_instrument=None):
    for s in app_data["students"]:
        if s["id"] == student_id:
            if new_name:
                s["name"] = new_name
            if new_instrument:
                s["instrument"] = new_instrument
            print(f"Student {student_id} updated.")
            return
    print("Student not found.")

def remove_student(student_id):
    for s in app_data["students"]:
        if s["id"] == student_id:
            app_data["students"].remove(s)
            print(f"Student {student_id} removed.")
            return
    print("Student not found.")
