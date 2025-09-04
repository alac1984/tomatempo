import json

from tomatempo.logs import LOGGER


def test_json_formatter_formats_record(log_record, json_formatter):
    """
    Ensure that JSONFormatter correctly formats a LogRecord into a JSON string
    containing expected keys (message, timestamp, level, etc.).
    """

    result = json_formatter.format(log_record)

    assert result is not None
    assert isinstance(result, str)
    assert json.loads(result)

    data = json.loads(result)

    assert data["level"] == "DEBUG"
    assert data["message"] == "This is a test"
    assert data["timestamp"] == "2023-01-01T12:00:00+00:00"
    assert data["logger"] == "test"
    assert data["line"] == 10
    assert data["thread_name"] == "MainThread"
    assert "exc_info" not in data
    assert "stack_info" not in data


def test_json_formatter_includes_extra_fields(caplog, json_formatter):
    """
    Verify that JSONFormatter includes custom extra fields passed to a log record.
    """

    LOGGER.warning("This is a message", extra={"test_field": "This is a test field"})

    record = caplog.records[0]

    result = json_formatter.format(record)
    data = json.loads(result)

    assert data["message"] == "This is a message"
    assert data["test_field"] == "This is a test field"


def test_json_formatter_handles_exceptions(caplog, json_formatter):
    """
    Check that JSONFormatter properly serializes exception and stack information when present.
    """

    def division_by_zero():
        return 0 / 0

    try:
        division_by_zero()
    except ZeroDivisionError as e:
        LOGGER.exception(e)

    assert "division by zero" in caplog.text


def test_non_error_filter_allows_info_and_below():
    """
    Ensure that NonErrorFilter allows DEBUG and INFO log records.
    """
    # TODO
    ...


def test_non_error_filter_blocks_warning_and_above():
    """
    Ensure that NonErrorFilter blocks WARNING, ERROR, and CRITICAL log records.
    """
    # TODO
    ...


def test_setup_logging_creates_log_file():
    """
    Confirm that setup_logging creates the expected log directory and file handler output file.
    """
    # TODO
    ...


def test_setup_logging_replaces_log_level():
    """
    Verify that setup_logging applies the configured log level from Settings to the root logger.
    """
    # TODO
    ...


def test_queue_listener_is_started():
    """
    Ensure that setup_logging attaches a QueueListener and that it is started.
    """
    # TODO
    ...


def test_queue_handler_passes_logs_to_targets():
    """
    Check that log messages sent to the QueueHandler are passed to target handlers.
    """
    # TODO
    ...


def test_at_exit_listener_stops():
    """
    Verify that the QueueListener is stopped on interpreter exit (atexit hook).
    """
    # TODO
    ...


def test_logging_yaml_formatters_are_loaded():
    """
    Confirm that the YAML configuration file correctly initializes both the 'simple' and 'json' formatters.
    """
    # TODO
    ...
