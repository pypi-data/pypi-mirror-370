import json
import traceback
from datetime import datetime
from typing import Any, Dict, List, Tuple, Union
from logfire import log as logfire_log
from pydantic import BaseModel

from .config import settings, LOG_FILE


def _write_jsonl(level: str, message: str, attributes: dict) -> None:
    """Write structured log entry to local JSONL file."""
    entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "level": level,
        "message": message,
        **attributes,
    }
    try:
        with LOG_FILE.open("a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")
    except Exception as e:
        print(f"[ERROR] Failed to write log: {e}")


def _safe_logfire(level: str, message: str, attributes: dict) -> None:
    """Safely log to Logfire with failover."""
    try:
        logfire_log(level, message, attributes)
    except Exception as e:
        print(f"[WARNING] Logfire logging failed: {e}")


def _log(level: str, message: str, data: Union[BaseModel, dict, None]) -> None:
    attributes = data.model_dump() if isinstance(data, BaseModel) else (data or {})
    _safe_logfire(level, message, attributes)
    _write_jsonl(level, message, attributes)


def log_info(message: str, data: Union[BaseModel, dict, None] = None) -> None:
    _log("info", message, data)


def log_warning(message: str, data: Union[BaseModel, dict, None] = None) -> None:
    _log("warning", message, data)


def log_error(message: str, data: Union[BaseModel, dict, None] = None) -> None:
    _log("error", message, data)


def log_exception(
    message: str, exc: Exception, data: Union[BaseModel, dict, None] = None
) -> None:
    error_data = {
        "exception": str(exc),
        "traceback": traceback.format_exc(),
        **(data.model_dump() if isinstance(data, BaseModel) else data or {}),
    }
    _log("error", message, error_data)
