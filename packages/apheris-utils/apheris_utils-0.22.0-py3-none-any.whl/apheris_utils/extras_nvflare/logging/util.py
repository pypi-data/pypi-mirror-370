import sys
import traceback
from dataclasses import dataclass
from typing import Callable, Literal, Optional

from nvflare.apis.fl_component import FLComponent

LogLevel = Literal["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG"]


def get_logger_fn_for_level(component: FLComponent, level: LogLevel) -> Callable:
    if level == "CRITICAL":
        return component.log_critical
    elif level == "ERROR":
        return component.log_error
    elif level == "WARNING":
        return component.log_warning
    elif level == "DEBUG":
        return component.log_debug
    else:
        return component.log_info


@dataclass
class ExceptionData:
    type: str
    line: Optional[str] = None
    function_name: Optional[str] = None
    filename: Optional[str] = None
    line_number: Optional[int] = None


def extract_exception_data() -> ExceptionData:
    """
    Call from inside an active exception to extract key information but hide the full
    stacktrace. Can be used to create sanitised error messages to send from the client
    to the server.
    """

    # We explicitly don't extract the exc_value as this can include sensitive
    # information
    exc_type, _, exc_traceback = sys.exc_info()
    tb = traceback.extract_tb(exc_traceback)

    return ExceptionData(
        line=tb[-1].line,
        function_name=tb[-1].name,
        filename=tb[-1].filename,
        line_number=tb[-1].lineno,
        type=exc_type.__name__ if exc_type else "Unknown",
    )


def format_exception_data(d: ExceptionData) -> str:
    return (
        f"Exception of type '{d.type}' has occurred in"
        f" {d.filename}:{d.line_number} (function: '{d.function_name}').\n"
        f"The exception was caused by the line '{d.line}'"
    )


def sanitised_trace() -> str:
    return format_exception_data(extract_exception_data())
