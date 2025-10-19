# gui/finance_pages.py
import streamlit as st
import pandas as pd
from decimal import Decimal, InvalidOperation
from datetime import datetime


METHOD_LABELS = [
    "Cash",
    "Credit Card",
    "Debit Card",
    "Bank Transfer",
    "Online Banking",
    "Touch 'n Go",
    "GrabPay",
    "Boost",
    "ShopeePay",
    "Other",
]

METHOD_PRETTY = {
    "cash": "Cash",
    "card": "Card",
    "transfer": "Bank Transfer",
    "ewallet": "E-wallet",
}


def _format_rm(value) -> str:
    try:
        amt = Decimal(str(value))
        return f"RM {amt:.2f}"
    except Exception:
        return str(value)


def _pretty_method(m: str | None) -> str:
    return METHOD_PRETTY.get(str(m), str(m))


def show_finance_page(manager):
    st.title("Finance & Payments")

    if not manager.students:
        st.info("No students found. Add students first to use Finance.")
        return

    # student maps
    students_map = {s.name: s.id for s in manager.students}
    id_to_name = {s.id: s.name for s in manager.students}
    student_names = sorted(students_map.keys(), key=str.casefold)

    # --- Record a Payment ---
    st.header("💳 Record New Payment")
    with st.form("payment_form", clear_on_submit=True):
        sel_name = st.selectbox("Student", student_names)
        amount = st.number_input(
            "Amount (RM)", min_value=0.01, step=0.01, format="%.2f")
        method_label = st.selectbox("Method", METHOD_LABELS)
        other_method = st.text_input(
            "If 'Other', specify", disabled=(method_label != "Other"))

        submit = st.form_submit_button("Record Payment")
        if submit:
            method_final = other_method.strip() if method_label == "Other" else method_label
            if not method_final:
                st.warning("Enter a payment method.")
            else:
                try:
                    amt = Decimal(f"{amount:.2f}")
                    if amt <= 0:
                        raise InvalidOperation
                except (InvalidOperation, ValueError):
                    st.error("Amount must be a positive number.")
                    return

                # Optional pre-check using manager's normalizer
                norm = getattr(manager, "_normalize_method", None)
                if callable(norm):
                    normalized = norm(method_final)
                    if normalized is None:
                        st.error(
                            "Unsupported payment method. Try Cash, Card (Credit/Debit), "
                            "Bank Transfer/Online Banking, or an e-wallet (Touch 'n Go, GrabPay, Boost, ShopeePay)."
                        )
                        return

                ok = manager.record_payment(
                    students_map[sel_name], f"{amt:.2f}", method_final)
                if ok:
                    st.success(f"Recorded {_format_rm(amt)} for {sel_name}.")
                else:
                    st.error(
                        "Failed to record payment (check student ID or logs).")

    st.divider()

    # --- Per-Student History ---
    st.header("View Payment History")
    hist_name = st.selectbox("Student", student_names, key="history_student")
    if hist_name:
        sid = students_map[hist_name]
        history = manager.get_payment_history(sid)
        if history:
            rows = []
            for rec in history:
                ts = rec.get("timestamp")
                rows.append(
                    {
                        "Timestamp": pd.to_datetime(ts).strftime("%Y-%m-%d %H:%M") if ts else "",
                        "Amount": _format_rm(rec.get("amount", "")),
                        "Method": _pretty_method(rec.get("method")),
                    }
                )
            st.dataframe(pd.DataFrame(rows), use_container_width=True)
            try:
                total = sum(Decimal(str(r.get("amount"))) for r in history)
                st.caption(f"Total for {hist_name}: {_format_rm(total)}")
            except Exception:
                pass
        else:
            st.info("No payments found for this student.")

    st.divider()

    # --- Recent Payments (All Students) ---
    st.header("Recent Payments (All Students)")
    if manager.finance_log:
        raw = []
        for rec in manager.finance_log:
            sid = rec.get("student_id")
            ts = rec.get("timestamp")
            raw.append(
                {
                    "Timestamp": pd.to_datetime(ts) if ts else None,
                    "Student": id_to_name.get(sid, f"Student #{sid}"),
                    "AmountRaw": str(rec.get("amount", "")),
                    "Amount": _format_rm(rec.get("amount", "")),
                    "Method": _pretty_method(rec.get("method")),
                }
            )
        df_all = pd.DataFrame(raw).sort_values("Timestamp", ascending=False)

        cols = st.columns([2, 1, 1])
        with cols[0]:
            term = st.text_input("Search (student or method)",
                                 placeholder="e.g., Alice, Cash, Card")
        with cols[1]:
            n_show = st.number_input(
                "Show last N", min_value=5, max_value=100, value=10, step=5)
        with cols[2]:
            only_today = st.checkbox("Today only")

        df_view = df_all.copy()
        if term:
            t = term.lower()
            df_view = df_view[
                df_view["Student"].str.lower().str.contains(
                    t) | df_view["Method"].str.lower().str.contains(t)
            ]
        if only_today:
            today_str = datetime.now().strftime("%Y-%m-%d")
            df_view = df_view[df_view["Timestamp"].dt.strftime(
                "%Y-%m-%d") == today_str]

        shown = df_view.head(int(n_show)).copy()
        shown["Timestamp"] = shown["Timestamp"].dt.strftime("%Y-%m-%d %H:%M")
        st.dataframe(shown[["Timestamp", "Student", "Amount",
                     "Method"]], use_container_width=True)

        try:
            subtotal = sum(Decimal(a) for a in shown["AmountRaw"])
            st.caption(f"Subtotal for shown rows: {_format_rm(subtotal)}")
        except Exception:
            pass
    else:
        st.info("No finance data yet.")

    st.divider()

    # --- Method Breakdown ---
    st.header("Method Breakdown")
    if manager.finance_log:
        df_m = pd.DataFrame(manager.finance_log)
        df_m["method"] = df_m["method"].astype(str)
        df_m["amount"] = df_m["amount"].astype(str)

        def _sum_decimal(series):
            try:
                return sum(Decimal(str(x)) for x in series)
            except Exception:
                return Decimal("0.00")

        grouped = (
            df_m.groupby("method", dropna=False)
            .agg(count=("method", "size"), total=("amount", _sum_decimal))
            .reset_index()
        )
        grouped["Method"] = grouped["method"].apply(_pretty_method)
        grouped["Total (RM)"] = grouped["total"].apply(
            lambda x: f"{Decimal(x):.2f}")
        grouped = grouped.sort_values("total", ascending=False)

        st.dataframe(grouped[["Method", "count", "Total (RM)"]].rename(columns={"count": "Count"}),
                     use_container_width=True)
        st.bar_chart(grouped.set_index("Method")[
                     ["total"]], use_container_width=True)
    else:
        st.info("No data to chart yet.")

    st.divider()

    # --- Export Downloads (in-app) ---
    st.header("Export Reports")
    ts = datetime.now().strftime("%Y%m%d_%H%M")

    col1, col2 = st.columns(2)
    with col1:
        if manager.finance_log:
            fin_csv = pd.DataFrame(manager.finance_log).to_csv(
                index=False).encode("utf-8")
            st.download_button(
                "Download Finance CSV",
                data=fin_csv,
                file_name=f"finance_{ts}.csv",
                mime="text/csv",
                use_container_width=True,
            )
        else:
            st.info("No finance data to export yet.")
    with col2:
        if manager.attendance_log:
            att_csv = pd.DataFrame(manager.attendance_log).to_csv(
                index=False).encode("utf-8")
            st.download_button(
                "Download Attendance CSV",
                data=att_csv,
                file_name=f"attendance_{ts}.csv",
                mime="text/csv",
                use_container_width=True,
            )
        else:
            st.info("No attendance data to export yet.")

    # Optional: write to disk using manager.export_report
    with st.expander("Write to disk (optional)"):
        out_dir = st.text_input("Folder", value="exports")
        kind = st.radio("Kind", ["Finance", "Attendance"], horizontal=True)
        if st.button("Write CSV to folder"):
            key = "finance" if kind == "Finance" else "attendance"
            path = f"{out_dir}/{key}_{ts}.csv"
            ok = manager.export_report(key, path)
            st.success(f"Saved: {path}") if ok else st.error(
                "Could not write CSV. See logs.")
