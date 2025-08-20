import inspect

from hakisto import logger
from ._logger_globals import logger_globals

logger_globals.register_excluded_source_file(inspect.currentframe().f_code.co_filename)


__all__ = [
    "hakisto_file",
    "hakisto_inline_location",
    "hakisto_process_all",
    "hakisto_process_file",
    "hakisto_process_inline_location",
    "hakisto_process_severity",
    "hakisto_process_short_trace",
    "hakisto_process_short_trace",
    "hakisto_severity",
    "hakisto_short_trace",
    "hakisto_use_color",
]

try:
    # noinspection PyPackageRequirements
    import click  # noqa: F401
except ImportError as e:
    logger.critical("package 'click' not found")
    raise e from None
else:
    from .click import (
        hakisto_file,
        hakisto_inline_location,
        hakisto_process_all,
        hakisto_process_file,
        hakisto_process_inline_location,
        hakisto_process_severity,
        hakisto_process_short_trace,
        hakisto_severity,
        hakisto_short_trace,
        hakisto_use_color,
    )
