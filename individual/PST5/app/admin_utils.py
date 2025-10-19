# app/admin_utils.py
from __future__ import annotations

import logging
import shutil
import datetime as _dt
import os
from logging.handlers import TimedRotatingFileHandler
from typing import Optional


_LOGGER_NAME = "msms"


def _get_logger() -> logging.Logger:
    """Return the app's named logger (singleton)."""
    return logging.getLogger(_LOGGER_NAME)


def init_logger(
    log_dir: str = "logs",
    log_file: str = "msms.log",
    level: int = logging.INFO,
    keep_days: int = 7,
    also_console: bool = True,
) -> str:
    """
    Initialize a robust logger for the app.

    - Writes to logs/<log_file>, rotating daily at midnight (keeps `keep_days` backups).
    - Optionally also logs to console (Streamlit will mirror console output).
    - Safe to call multiple times: no duplicate handlers.

    Returns the absolute path to the current log file.
    """
    os.makedirs(log_dir, exist_ok=True)
    log_path = os.path.join(log_dir, log_file)
    logger = _get_logger()
    logger.setLevel(level)
    logger.propagate = False  # don't bubble into root

    # Deduplicate handlers across reruns
    existing_files = [h for h in logger.handlers if isinstance(
        h, TimedRotatingFileHandler)]
    existing_streams = [
        h for h in logger.handlers if isinstance(h, logging.StreamHandler)]

    if not existing_files:
        file_handler = TimedRotatingFileHandler(
            filename=log_path,
            when="midnight",
            interval=1,
            backupCount=max(int(keep_days), 0),
            encoding="utf-8",
            utc=False,
        )
        file_handler.setLevel(level)
        file_handler.setFormatter(logging.Formatter(
            "%(asctime)s - %(levelname)s - %(message)s"))
        logger.addHandler(file_handler)

    if also_console and not existing_streams:
        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(level)
        stream_handler.setFormatter(
            logging.Formatter("%(levelname)s - %(message)s"))
        logger.addHandler(stream_handler)

    logger.info("Logger initialized. File: %s", os.path.abspath(log_path))
    return os.path.abspath(log_path)


def backup_data(
    data_path: str = "data/msms.json",
    backup_dir: str = "data/backups"
) -> Optional[str]:
    """
    Copy data_path → backup_dir/backup_<timestamp>.json.

    Returns the backup file path on success, or None on failure.
    If `data_path` does not exist, creates an empty JSON file and backs that up.
    """
    logger = _get_logger()
    os.makedirs(backup_dir, exist_ok=True)

    # Ensure source exists (create an empty JSON if missing)
    if not os.path.exists(data_path):
        try:
            os.makedirs(os.path.dirname(data_path) or ".", exist_ok=True)
            with open(data_path, "w", encoding="utf-8") as f:
                f.write("{}")
            logger.warning(
                "%s did not exist. Created an empty JSON file.", data_path)
        except Exception as e:
            logger.error("Could not create %s: %s", data_path, e)
            return None

    ts = _dt.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    backup_path = os.path.join(backup_dir, f"backup_{ts}.json")

    try:
        shutil.copy2(data_path, backup_path)  # preserves mtime/permissions
        logger.info("Data successfully backed up to %s",
                    os.path.abspath(backup_path))
        return backup_path
    except Exception as e:
        logger.error("Failed to create backup from %s to %s: %s",
                     data_path, backup_path, e)
        return None
