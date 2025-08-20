from .file import hakisto_file, hakisto_process_file
from .inline_location import hakisto_inline_location, hakisto_process_inline_location
from .severity import hakisto_severity, hakisto_process_severity
from .short_trace import hakisto_short_trace, hakisto_process_short_trace
from .use_color import hakisto_use_color, hakisto_process_use_color

__all__ = [
    "hakisto_file",
    "hakisto_inline_location",
    "hakisto_process_all",
    "hakisto_process_file",
    "hakisto_process_inline_location",
    "hakisto_process_severity",
    "hakisto_process_short_trace",
    "hakisto_severity",
    "hakisto_short_trace",
    "hakisto_use_color",
]

PROCESSOR = dict(
    log_file=hakisto_process_file,
    log_inline_location=hakisto_process_inline_location,
    log_severity=hakisto_process_severity,
    log_short_trace=hakisto_process_short_trace,
    log_use_color=hakisto_process_use_color,
)


def hakisto_process_all(**kwargs):
    """Process all Hakisto options."""

    if "log_file" in kwargs:
        hakisto_process_file(kwargs["log_file"])
    if "log_inline_location" in kwargs:
        hakisto_process_inline_location(kwargs["log_inline_location"])
    if "log_severity" in kwargs:
        hakisto_process_severity(kwargs["log_severity"])
    if "log_short_trace" in kwargs:
        hakisto_process_short_trace(kwargs["log_short_trace"])
    if "log_use_color" in kwargs:
        hakisto_use_color(kwargs["log_use_color"])


# __import__("pkg_resources").declare_namespace(__name__)  # pragma: no cover
