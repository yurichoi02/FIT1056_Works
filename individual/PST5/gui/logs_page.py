# gui/logs_page.py
import os
from collections import deque
import streamlit as st


DEFAULT_LOG_PATH = "logs/msms.log"


def view_logs_page():
    st.title("📜 System Logs")

    if st.session_state.get("role") != "admin":
        st.error("Admin only. Please sign in with the admin PIN in the sidebar.")
        return

    log_path = DEFAULT_LOG_PATH

    cols = st.columns([3, 1, 1])
    with cols[0]:
        st.caption(f"Log file: `{os.path.abspath(log_path)}`")
    with cols[1]:
        if st.button("🔄 Refresh", use_container_width=True):
            try:
                st.rerun()
            except Exception:
                st.experimental_rerun()
    with cols[2]:
        if st.button("🗑️ Clear Logs", use_container_width=True):
            try:
                os.makedirs(os.path.dirname(log_path) or ".", exist_ok=True)
                with open(log_path, "w", encoding="utf-8") as f:
                    f.write("")
                st.success("Log file cleared.")
                try:
                    st.rerun()
                except Exception:
                    st.experimental_rerun()
            except Exception as e:
                st.error(f"Could not clear logs: {e}")

    if not os.path.exists(log_path):
        st.info(
            "No logs found yet. Try recording a payment or cancelling a lesson to generate logs.")
        return

    # Tail efficiently
    q = deque(maxlen=800)
    try:
        with open(log_path, "r", encoding="utf-8", errors="replace") as f:
            for line in f:
                q.append(line.rstrip("\n"))
    except Exception as e:
        st.error(f"Failed to read log: {e}")
        return

    st.text_area("Log Output (read-only)", "\n".join(q)
                 if q else "(empty)", height=420, disabled=True)

    # Download
    try:
        with open(log_path, "rb") as fh:
            st.download_button(
                "⬇️ Download full log",
                data=fh.read(),
                file_name=os.path.basename(log_path),
                mime="text/plain",
                use_container_width=True,
            )
    except Exception as e:
        st.error(f"Download failed: {e}")
