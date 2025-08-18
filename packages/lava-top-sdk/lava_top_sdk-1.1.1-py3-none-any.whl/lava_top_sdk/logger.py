import logging
import json
from typing import Optional, Dict, Any
from enum import Enum
from datetime import datetime


class LogLevel(str, Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class LogFormat(str, Enum):
    JSON = "json"
    TEXT = "text"


class Logger:
    def __init__(
        self,
        level: LogLevel = LogLevel.INFO,
        format_type: LogFormat = LogFormat.TEXT,
        name: str = "lava_client",
    ):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, level.value))
        self.format_type = format_type

        # Remove existing handlers
        self.logger.handlers.clear()

        # Create handler
        handler = logging.StreamHandler()

        if format_type == LogFormat.JSON:
            handler.setFormatter(JsonFormatter())
        else:
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            handler.setFormatter(formatter)

        self.logger.addHandler(handler)

    def debug(self, message: str, extra: Optional[Dict[str, Any]] = None):
        self._log(logging.DEBUG, message, extra)

    def info(self, message: str, extra: Optional[Dict[str, Any]] = None):
        self._log(logging.INFO, message, extra)

    def warning(self, message: str, extra: Optional[Dict[str, Any]] = None):
        self._log(logging.WARNING, message, extra)

    def error(self, message: str, extra: Optional[Dict[str, Any]] = None):
        self._log(logging.ERROR, message, extra)

    def critical(self, message: str, extra: Optional[Dict[str, Any]] = None):
        self._log(logging.CRITICAL, message, extra)

    def _log(self, level: int, message: str, extra: Optional[Dict[str, Any]] = None):
        if self.format_type == LogFormat.JSON and extra:
            log_data = {
                "timestamp": datetime.utcnow().isoformat(),
                "message": message,
                "level": logging.getLevelName(level),
                **extra,
            }
            self.logger.log(level, json.dumps(log_data))
        else:
            extra_str = f" | {extra}" if extra else ""
            self.logger.log(level, f"{message}{extra_str}")


class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "logger": record.name,
        }

        # Add any extra fields
        if hasattr(record, "extra"):
            log_data.update(record.extra)

        return json.dumps(log_data)
