# msms.py — GUI Launcher
import os
from gui.main_dashboard import launch

# Try to import admin utils, but don't hard-fail if missing
try:
    from app.admin_utils import init_logger, backup_data  # type: ignore
except Exception:
    init_logger = None
    backup_data = None


def _ensure_dir(path: str) -> None:
    if path and not os.path.exists(path):
        os.makedirs(path, exist_ok=True)


if __name__ == "__main__":
    # --- Logging setup (optional) ---
    log_dir = "logs"
    log_file = "msms.log"
    _ensure_dir(log_dir)
    if init_logger:
        try:
            # creates logs/msms.log and sets console/file handlers
            init_logger(log_dir=log_dir, log_file=log_file)
        except Exception as e:
            # Fall through silently; Streamlit UI can still run
            print(f"[msms] init_logger failed: {e}")

    # --- One-off backup before UI (optional) ---
    data_path = "data/msms.json"
    backup_dir = "data/backups"
    _ensure_dir(os.path.dirname(data_path) or ".")
    _ensure_dir(backup_dir)
    if backup_data and os.path.exists(data_path):
        try:
            # copies data/msms.json → data/backups/...
            backup_data(data_path=data_path, backup_dir=backup_dir)
        except Exception as e:
            print(f"[msms] backup_data failed: {e}")

    # --- Launch Streamlit app ---
    launch()
