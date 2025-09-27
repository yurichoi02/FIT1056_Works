import streamlit as st
import pandas as pd


def show_roster_page(manager):
    st.header("Daily Roster")
    day = st.selectbox(
        "Select a day", ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"])
    rows = manager.daily_roster(day)
    if rows:
        teachers = sorted({r['teacher'] for r in rows if r.get('teacher')})
        picked = st.selectbox('Filter by teacher (optional)', [
                              '(All)'] + teachers)
        if picked != '(All)':
            rows = [r for r in rows if r.get('teacher') == picked]
        st.dataframe(pd.DataFrame(rows), use_container_width=True)
    else:
        st.info("No classes scheduled for this day.")
    st.markdown("---")
    st.subheader("Student Check-in")
    students = {f"{s.id} — {s.name}": s.id for s in manager.students}
    courses = {
        f"{c.id} — {c.name} ({c.instrument})": c.id for c in manager.courses}
    with st.form("check_in_form", clear_on_submit=True):
        selected_student = st.selectbox("Student", list(students.keys()))
        selected_course = st.selectbox("Course", list(courses.keys()))
        submitted = st.form_submit_button("Check-in Student")
    if submitted:
        ts = manager.check_in(
            students[selected_student], courses[selected_course])
        if ts:
            st.success(
                f"Checked in {selected_student} for {selected_course}! ({ts})")
        else:
            st.error("Check-in failed. Is the student enrolled in that course?")
    st.markdown("---")
    st.subheader("Export attendance")
    if st.session_state.get("role") == "admin":
        st.download_button("Download attendance CSV", data=manager.attendance_csv(),
                           file_name="attendance.csv", mime="text/csv")
    else:
        st.info("Sign in as admin from the sidebar to download attendance.")
