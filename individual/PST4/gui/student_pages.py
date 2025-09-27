import streamlit as st


def show_student_management_page(manager):
    st.header("Student Management")

    # --- Registration ---
    st.subheader("Register New Student")
    with st.form("registration_form", clear_on_submit=True):
        reg_name = st.text_input(
            "New Student Name", placeholder="e.g., Alice Tan")
        instruments = manager.available_instruments()
        reg_instrument = (
            st.selectbox("Instrument (from available courses)", instruments)
            if instruments else
            st.text_input("Instrument", placeholder="e.g., Piano")
        )
        submitted = st.form_submit_button("Register Student")
    if submitted:
        if reg_name and reg_instrument:
            sid = manager.register_new_student(reg_name, reg_instrument)
            if sid:
                st.success(f"Successfully registered {reg_name} (ID: {sid}).")
            else:
                st.error(
                    "Registration failed. Please check instrument or try again.")
        else:
            st.warning("Please enter both a name and an instrument.")

    # --- View all students ---
    with st.expander("View all students"):
        st.dataframe(manager.list_students(), use_container_width=True)

    # --- Search ---
    st.markdown("---")
    st.subheader("Find a Student")
    q = st.text_input("Search by name (case-insensitive)",
                      placeholder="e.g., ali")
    st.dataframe(manager.search_students(q), use_container_width=True)

    # --- Instrument summary ---
    with st.expander("Instrument summary (registered vs enrolled)"):
        st.dataframe(manager.instrument_summary(), use_container_width=True)

    # --- Enrol student (admin) ---
    st.markdown("---")
    st.subheader("Enroll student into course")
    if st.session_state.get("role") == "admin":
        stu_opts = {f"{s.id} — {s.name}": s.id for s in manager.students}
        crs_opts = {
            f"{c.id} — {c.name} ({c.instrument})": c.id for c in manager.courses}
        if stu_opts and crs_opts:
            stu_pick = st.selectbox("Student", list(
                stu_opts.keys()), key="enrol_student")
            crs_pick = st.selectbox("Course", list(
                crs_opts.keys()), key="enrol_course")
            if st.button("Enroll"):
                ok = manager.enrol_student_to_course(
                    stu_opts[stu_pick], crs_opts[crs_pick])
                st.success("Enrolled successfully.") if ok else st.error(
                    "Enrollment failed.")
        else:
            st.info("Need at least one student and one course to enroll.")
    else:
        st.info("Sign in as admin from the sidebar to perform enrollments.")

    # --- Edit/Delete Student (admin) ---
    if st.session_state.get("role") == "admin":
        st.markdown("---")
        with st.expander("Edit / Delete Student"):
            stu_opts_full = {f"{s.id} — {s.name}": s for s in manager.students}
            if stu_opts_full:
                sel_key = st.selectbox("Pick a student", list(
                    stu_opts_full.keys()), key="edit_student_pick")
                s_obj = stu_opts_full[sel_key]
                new_name = st.text_input("Name", value=s_obj.name)
                new_pref = st.text_input("Preferred instrument", value=getattr(
                    s_obj, "preferred_instrument", "") or "")

                c1, c2 = st.columns(2)
                with c1:
                    if st.button("Save changes", key="save_student_changes"):
                        ok = manager.edit_student(
                            s_obj.id, name=new_name, preferred_instrument=new_pref)
                        if ok:
                            st.success("Student updated.")
                            st.rerun()
                        else:
                            st.error("Update failed.")
                with c2:
                    confirm_student = st.checkbox(
                        "I’m sure", key=f"confirm_del_student_{s_obj.id}")
                    if st.button("Delete student", key="delete_student_confirm", disabled=not confirm_student):
                        ok = manager.delete_student(s_obj.id)
                        if ok:
                            st.success("Student deleted.")
                            st.rerun()
                        else:
                            st.error("Delete failed.")
    else:
        st.info("Sign in as admin from the sidebar to edit or delete students.")
