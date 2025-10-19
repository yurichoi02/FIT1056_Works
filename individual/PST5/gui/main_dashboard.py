# gui/main_dashboard.py
import os
import re
import streamlit as st

from app.schedule import ScheduleManager

from gui.student_pages import show_student_management_page
from gui.roster_pages import show_roster_page
from gui.teacher_pages import show_teacher_management_page
from gui.finance_pages import show_finance_page
from gui.logs_page import view_logs_page

# Guarded import for optional admin utilities
try:
    from app.admin_utils import backup_data  # type: ignore
except Exception:
    backup_data = None


def _get_admin_pin_default_safe() -> str:
    """ADMIN_PIN from secrets → env → default '123456'."""
    try:
        val = st.secrets.get("ADMIN_PIN", None)  # type: ignore[attr-defined]
        if val is not None:
            return str(val)
    except Exception:
        pass
    return str(os.getenv("ADMIN_PIN", "123456"))


def launch():
    st.set_page_config(
        layout="wide", page_title="Music School Management System")

    # --- Auth ---
    with st.sidebar.expander("Sign in"):
        if "role" not in st.session_state:
            st.session_state.role = "guest"

        pin = st.text_input("Admin PIN (6 digits)",
                            type="password", placeholder="••••••")
        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("Sign in as admin"):
                expected = _get_admin_pin_default_safe()
                if re.fullmatch(r"\d{6}", pin or "") and pin == expected:
                    st.session_state.role = "admin"
                    st.success("Signed in as admin")
                else:
                    st.error("Invalid PIN (must be exactly 6 digits)")
        with col_b:
            if st.button("Sign out"):
                st.session_state.role = "guest"

    is_admin = st.session_state.get("role") == "admin"
    st.sidebar.caption(f"Role: **{st.session_state.role}**")

    # --- Admin tools ---
    with st.sidebar.expander("Admin Tools"):
        if st.button("🗂️ Backup Now", disabled=not is_admin):
            if backup_data is None:
                st.error("Backup utility not available.")
            else:
                try:
                    result = backup_data()  # True/False or path string
                    if result:
                        msg = f"Backup created: {result}" if isinstance(
                            result, str) else "Backup created."
                        st.success(msg)
                    else:
                        st.error("Backup failed. Check logs.")
                except Exception as e:
                    st.error(f"Backup error: {e}")
        if not is_admin:
            st.caption("Sign in as admin to use tools.")

    # --- Singleton manager ---
    if "manager" not in st.session_state:
        st.session_state.manager = ScheduleManager()

    # --- Navigation (Payments + System Logs only for admins) ---
    st.sidebar.title("MSMS Navigation")
    pages_all = ["Student Management", "Teacher Management",
                 "Daily Roster", "Payments", "System Logs"]
    pages_non_admin = ["Student Management",
                       "Teacher Management", "Daily Roster"]
    pages = pages_all if is_admin else pages_non_admin
    page = st.sidebar.radio("Go to", pages, index=0)

    # --- Router ---
    if page == "Student Management":
        show_student_management_page(st.session_state.manager)
    elif page == "Teacher Management":
        show_teacher_management_page(st.session_state.manager)
    elif page == "Daily Roster":
        show_roster_page(st.session_state.manager)
    elif page == "Payments":       # admin only (hidden for guests)
        show_finance_page(st.session_state.manager)
    elif page == "System Logs":    # admin only
        view_logs_page()
