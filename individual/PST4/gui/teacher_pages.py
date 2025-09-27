import streamlit as st


def show_teacher_management_page(manager):
    st.header("Teacher Management")

    if st.session_state.get("role") != "admin":
        st.info("Sign in as admin from the sidebar to manage teachers and courses.")
        can_admin = False
    else:
        can_admin = True

    # ---------- Add Teacher ----------
    st.subheader("Add Teacher")
    with st.form("add_teacher_form", clear_on_submit=True):
        t_name = st.text_input(
            "Teacher name", placeholder="e.g., Ms. Viola Chen")
        t_spec = st.text_input("Speciality", placeholder="e.g., Violin")
        submitted_add_t = st.form_submit_button("Create teacher")
    if submitted_add_t:
        if not can_admin:
            st.error("Admin sign-in required.")
        elif not (t_name and t_spec):
            st.error("Please fill in both name and speciality.")
        elif any(t_name.strip().casefold() == t.name.casefold() for t in manager.teachers):
            st.error("A teacher with this name already exists.")
        else:
            tid = manager.add_teacher(t_name, t_spec)
            if tid:
                st.success(f"Teacher created (ID: {tid})")
                st.rerun()
            else:
                st.error("Could not create teacher (duplicate or invalid).")

    st.markdown("---")

    # ---------- Add Course ----------
    st.subheader("Add Course")
    with st.form("add_course_form", clear_on_submit=True):
        c_name = st.text_input("Course name")
        c_instr = st.text_input("Instrument", placeholder="e.g., Violin")
        teacher_opts = {
            f"{t.id} — {t.name} ({t.speciality})": t.id for t in manager.teachers}
        t_pick = st.selectbox("Assign teacher", list(
            teacher_opts.keys())) if teacher_opts else None
        c_day = st.selectbox(
            "Day", ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"])
        c_start = st.text_input("Start time (HH:MM)", placeholder="17:00")
        c_room = st.text_input("Room", placeholder="Room C")
        submitted_add_c = st.form_submit_button("Create course")
    if submitted_add_c:
        if not can_admin:
            st.error("Admin sign-in required.")
        elif not t_pick:
            st.error("Add or select a teacher first.")
        elif not (c_name and c_instr and c_day and c_start and c_room):
            st.error("Please complete all course fields.")
        elif any(c_name.strip().casefold() == c.name.casefold() for c in manager.courses):
            st.error("A course with this name already exists.")
        elif not manager._is_valid_time(c_start):
            st.error("Use HH:MM 24-hour time (e.g., 09:00, 17:30).")
        else:
            cid = manager.add_course(
                c_name, c_instr, teacher_opts[t_pick], c_day, c_start, c_room)
            if cid:
                st.success(f"Course created (ID: {cid})")
                st.rerun()
            else:
                st.error(
                    "Could not create course (duplicate, invalid time, or teacher slot clash).")

    st.markdown("---")

    # ---------- Teacher List ----------
    st.subheader("All Teachers")
    tdata = [{"id": t.id, "name": t.name, "speciality": t.speciality}
             for t in manager.teachers]
    if tdata:
        st.dataframe(tdata, use_container_width=True)
    else:
        st.info("No teachers yet.")

    st.markdown("---")

    # ---------- Edit / Delete Teacher ----------
    st.subheader("Edit / Delete Teacher")
    tmap = {f"{t.id} — {t.name} ({t.speciality})": t for t in manager.teachers}
    if not tmap:
        st.info("No teachers to edit.")
        return
    pick = st.selectbox("Pick a teacher", list(tmap.keys()))
    teacher = tmap[pick]

    colA, colB = st.columns(2)
    with colA:
        new_name = st.text_input(
            "Teacher name", value=teacher.name, disabled=not can_admin)
    with colB:
        new_spec = st.text_input(
            "Speciality", value=teacher.speciality, disabled=not can_admin)

    c1, c2 = st.columns(2)
    with c1:
        if st.button("Save teacher changes", disabled=not can_admin):
            if not (new_name and new_spec):
                st.error("Please fill in both name and speciality.")
            elif any(new_name.strip().casefold() == t.name.casefold() and t.id != teacher.id for t in manager.teachers):
                st.error("A teacher with this name already exists.")
            else:
                ok = manager.edit_teacher(
                    teacher.id, name=new_name, speciality=new_spec)
                if ok:
                    st.success("Teacher updated.")
                    st.rerun()
                else:
                    st.error("Update failed.")
    with c2:
        owns_courses = [
            c for c in manager.courses if c.teacher_id == teacher.id]
        if owns_courses:
            st.warning(
                "This teacher still has assigned courses. Reassign them first to enable deletion.")
            st.button("Delete teacher", disabled=True)
        else:
            confirm_teacher = st.checkbox(
                "I’m sure", key=f"confirm_del_teacher_{teacher.id}")
            if st.button("Delete teacher", disabled=not can_admin or not confirm_teacher):
                ok = manager.delete_teacher(teacher.id)
                if ok:
                    st.success("Teacher deleted.")
                    st.rerun()
                else:
                    st.error("Delete failed.")

    st.markdown("---")

    # ---------- Edit / Delete Course ----------
    st.subheader("Edit / Delete Course")
    crs_opts_full = {
        f"{c.id} — {c.name} ({c.instrument})": c for c in manager.courses}
    if not crs_opts_full:
        st.info("No courses to edit.")
    else:
        selc_key = st.selectbox("Pick a course", list(
            crs_opts_full.keys()), key="edit_course_pick_tm")
        c_obj = crs_opts_full[selc_key]
        cur_day = c_obj.lessons[0].get("day") if c_obj.lessons else "Monday"
        cur_time = c_obj.lessons[0].get(
            "start_time") if c_obj.lessons else "09:00"
        cur_room = c_obj.lessons[0].get("room") if c_obj.lessons else "Room A"

        new_c_name = st.text_input("Course name", value=c_obj.name)
        new_instr = st.text_input("Instrument", value=c_obj.instrument)
        teacher_opts2 = {
            f"{t.id} — {t.name} ({t.speciality})": t.id for t in manager.teachers}
        new_teacher_pick = st.selectbox("Teacher", list(
            teacher_opts2.keys())) if teacher_opts2 else None
        new_day = st.selectbox("Day", ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
                               index=["Monday", "Tuesday", "Wednesday",
                                      "Thursday", "Friday"].index(cur_day)
                               if cur_day in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"] else 0)
        new_time = st.text_input("Start time (HH:MM)", value=cur_time)
        new_room = st.text_input("Room", value=cur_room)

        c1b, c2b = st.columns(2)
        with c1b:
            if st.button("Save course changes", key="save_course_changes_tm", disabled=not can_admin):
                tid = teacher_opts2[new_teacher_pick] if new_teacher_pick else None
                ok = manager.edit_course(
                    c_obj.id, name=new_c_name, instrument=new_instr, teacher_id=tid,
                    day=new_day, start_time=new_time, room=new_room,
                )
                if ok:
                    st.success("Course updated.")
                    st.rerun()
                else:
                    st.error(
                        "Update failed (duplicate name, invalid time, or teacher clash).")
        with c2b:
            confirm_course = st.checkbox(
                "I’m sure", key=f"confirm_del_course_tm_{c_obj.id}")
            if st.button("Delete course", key="delete_course_confirm_tm", disabled=not can_admin or not confirm_course):
                ok = manager.delete_course(c_obj.id)
                if ok:
                    st.success("Course deleted.")
                    st.rerun()
                else:
                    st.error("Delete failed.")

    st.markdown("---")

    # ---------- Reassign Course Teacher ----------
    st.subheader("Reassign Course Teacher")
    my_courses = [c for c in manager.courses if c.teacher_id == teacher.id]
    if not my_courses:
        st.info("Selected teacher has no courses to reassign.")
        return
    course_opts = {
        f"{c.id} — {c.name} ({c.instrument})": c for c in my_courses}
    sel_course = st.selectbox("Course", list(course_opts.keys()))
    course = course_opts[sel_course]
    target_teachers = {
        f"{t.id} — {t.name} ({t.speciality})": t.id for t in manager.teachers if t.id != teacher.id}
    if not target_teachers:
        st.info("No other teachers available to reassign to.")
        return
    new_t_pick = st.selectbox("New teacher", list(target_teachers.keys()))
    if course.lessons:
        cur_day2 = course.lessons[0].get("day", "")
        cur_time2 = course.lessons[0].get("start_time", "")
        st.caption(
            f"Course slot: **{cur_day2} {cur_time2}** — reassignment checks for teacher time clashes.")
    if st.button("Reassign", disabled=not can_admin):
        ok = manager.reassign_course_teacher(
            course.id, target_teachers[new_t_pick])
        if ok:
            st.success("Course reassigned.")
            st.rerun()
        else:
            st.error("Reassignment failed (time clash or invalid teacher).")
