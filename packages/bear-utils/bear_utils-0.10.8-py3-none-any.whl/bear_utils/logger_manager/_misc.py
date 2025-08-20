from logging import LogRecord

from bear_utils.logger_manager._constants import ExecValues, LoggerExtraInfo


def get_extra(record: LogRecord) -> LoggerExtraInfo:
    """Get extra information from the log record."""
    extra: LoggerExtraInfo = {
        "style_name": record.__dict__.get("style_name", ""),
        "style": record.__dict__.get("style", ""),
        "log_level": record.__dict__.get("log_level", ""),
        "log_level_style": record.__dict__.get("log_level_style", ""),
        "namespace": record.__dict__.get("namespace", ""),
    }
    return extra


def extract_exec_info(record: LogRecord) -> dict[str, ExecValues] | None:
    """Extract execution info from the log record."""
    exec_values: dict[str, ExecValues] | None = record.__dict__.get("exec_values", {})
    if exec_values is not None:
        return exec_values
    return None
