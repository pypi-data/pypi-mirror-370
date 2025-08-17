"""
Thread-safe structured logging with JSON metadata.

Provides file-based logging with timestamp formatting and optional JSON metadata
for request context and performance tracking.
"""
import json
import os
from datetime import datetime
from threading import Lock
from typing import Any


class Logger:
    """Thread-safe file logger with structured JSON metadata support."""

    def __init__(self, log_dir: str, log_filename: str = "app.log") -> None:
        self.log_path = os.path.join(log_dir, log_filename)
        os.makedirs(log_dir, exist_ok=True)
        self.lock = Lock()

    def _write(self, level: str, message: str, **kwargs: Any) -> None:
        try:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            log_line = f"[{timestamp}] [{level}] {message}"

            if kwargs:
                data = json.dumps({k: v for k, v in kwargs.items() if v is not None},
                                  default=str, separators=(',', ':'))
                log_line += f" | {data}"

            with self.lock:
                with open(self.log_path, 'a', encoding='utf-8') as f:
                    f.write(log_line + '\n')
        except Exception:
            pass  # Logging failures should not break the app

    def debug(self, message: str, **kwargs: Any) -> None:
        self._write("DEBUG", message, **kwargs)

    def info(self, message: str, **kwargs: Any) -> None:
        self._write("INFO", message, **kwargs)

    def warning(self, message: str, **kwargs: Any) -> None:
        self._write("WARNING", message, **kwargs)

    def error(self, message: str, **kwargs: Any) -> None:
        self._write("ERROR", message, **kwargs)


def get_logger(log_dir: str = "logs") -> Logger:
    """Create logger instance with specified directory."""
    return Logger(log_dir)
