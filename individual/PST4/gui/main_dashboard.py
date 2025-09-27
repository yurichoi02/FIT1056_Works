import os
import re
import streamlit as st
from app.schedule import ScheduleManager
from gui.student_pages import show_student_management_page
from gui.roster_pages import show_roster_page
from gui.teacher_pages import show_teacher_management_page


def _get_admin_pin_default_safe():
    try:
        val = st.secrets["ADMIN_PIN"]
        return str(val)
    except Exception:
        return os.getenv("ADMIN_PIN", "123456")


def launch():
    st.set_page_config(
        layout="wide", page_title="Music School Management System")

    with st.sidebar.expander("Sign in"):
        if "role" not in st.session_state:
            st.session_state.role = "guest"
        pin = st.text_input("Admin PIN (6 digits)",
                            type="password", placeholder="••••••")
        if st.button("Sign in as admin"):
            expected = _get_admin_pin_default_safe()
            if re.fullmatch(r"\d{6}", pin or "") and pin == expected:
                st.session_state.role = "admin"
                st.success("Signed in as admin")
            else:
                st.error("Invalid PIN (must be exactly 6 digits)")
        if st.button("Sign out"):
            st.session_state.role = "guest"
    st.sidebar.caption(f"Role: {st.session_state.role}")

    if 'manager' not in st.session_state:
        st.session_state.manager = ScheduleManager()

    st.sidebar.title("MSMS Navigation")
    page = st.sidebar.radio("Go to", [
                            "Student Management", "Teacher Management", "Daily Roster", "Payments (stub)"])

    if page == "Student Management":
        show_student_management_page(st.session_state.manager)
    elif page == "Teacher Management":
        show_teacher_management_page(st.session_state.manager)
    elif page == "Daily Roster":
        show_roster_page(st.session_state.manager)
    else:
        st.header("Payments")
        st.warning("This feature will be implemented in PST5.")
