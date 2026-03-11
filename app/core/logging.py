import logging
import json
import sys
from datetime import datetime, timezone

class JSONFormatter(logging.Formatter):
    """
    Formats log records as JSON so CloudWatch can parse and query them.
    Every log line will be a valid JSON object.
    """
    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "logger": record.name,
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Add extra fields if present
        # These are injected by middleware — tenant_id, request_id etc
        for key in ["tenant_id", "request_id", "user_email", "path", "method", "status_code", "duration_ms"]:
            if hasattr(record, key):
                log_entry[key] = getattr(record, key)

        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_entry)


def setup_logging() -> None:
    """
    Configure logging for the entire application.
    Call this once at startup in main.py
    """
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    # Remove existing handlers
    root_logger.handlers.clear()

    # Console handler — ECS captures stdout and sends to CloudWatch
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JSONFormatter())
    root_logger.addHandler(handler)

    # Silence noisy libraries
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """Get a named logger. Use this everywhere instead of print()"""
    return logging.getLogger(name)