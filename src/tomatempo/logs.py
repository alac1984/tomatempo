import os
import json
import atexit
import logging
import logging.config
import logging.handlers
import datetime as dt
from pathlib import Path
from typing import override

from tomatempo.settings import Settings, get_settings

LOG_RECORD_BUILTIN_ATTRS = {
    "args",
    "asctime",
    "created",
    "exc_info",
    "exc_text",
    "filename",
    "funcName",
    "levelname",
    "levelno",
    "lineno",
    "module",
    "msecs",
    "message",
    "msg",
    "name",
    "pathname",
    "process",
    "processName",
    "relativeCreated",
    "stack_info",
    "thread",
    "threadName",
    "taskName",
}

class JSONFormatter(logging.Formatter):
    """
    Custom Formatter for compose logs in JSONLines format.
    """

    def __init__(self, *, fmt_keys: dict[str, str] | None = None):
        super().__init__()
        self.fmt_keys = fmt_keys if fmt_keys is not None else {}

    @override
    def format(self, record: logging.LogRecord) -> str:
        message = self._prepare_log_dict(record)
        return json.dumps(message, default=str)


    def _prepare_log_dict(self, record: logging.LogRecord) -> dict[str, str]:
        always_fields = {
            "message": record.getMessage(),
            "timestamp": dt.datetime.fromtimestamp(
                record.created, tz=dt.timezone.utc
            ).isoformat(),
        }

        if record.exc_info is not None:
            always_fields['exc_info'] = self.formatException(record.exc_info)

        if record.stack_info is not None:
            always_fields['stack_info'] = self.formatStack(record.stack_info)

        message = {
            key: msg_val
            if (msg_val := always_fields.pop(val, None)) is not None
            else getattr(record, val)
            for key, val in self.fmt_keys.items()
        }

        message.update(always_fields)

        for key, val in record.__dict__.items():
            if key not in LOG_RECORD_BUILTIN_ATTRS:
                message[key] = val

        return message


class NonErrorFilter(logging.Filter):
    @override
    def filter(self, record: logging.LogRecord) -> bool | logging.LogRecord:
        return record.levelno <= logging.INFO


_listener = None

def setup_logging(settings: Settings):
    # Make sure log directory exists
    Path(settings.logs_dir).mkdir(parents=True, exist_ok=True)

    # Load yaml and placeholders
    config_file = Path("./src/tomatempo/config/logging.yaml")
    
    import yaml  # type: ignore [import-untyped]

    with open(config_file) as f_in:
        cfg = yaml.safe_load(f_in)

        # Insert log dir
        cfg['handlers']['file_json']['filename'] = str(settings.logs_dir) + "/log_tomatempo.jsonl"

        # Insert log level in root
        cfg['root']['level'] = settings.log_level

    logging.config.dictConfig(cfg)
    
    # Get root logger
    root = logging.getLogger()
    # Get the queue handler
    qh = next(h for h in root.handlers if isinstance(h, logging.handlers.QueueHandler))
    # Get other handlers
    targets = [h for h in root.handlers if h is not qh]

    global _listener

    _listener = logging.handlers.QueueListener(qh.queue, *targets, respect_handler_level=True)
    _listener.start()

    # Remove targets from root to avoid duplicates
    for h in targets:
        root.removeHandler(h)

    # Clean and go out
    atexit.register(lambda: (_listener.stop() if _listener else None))


logger = logging.getLogger()
