import threading

from ._logger_globals import logger_globals
from .severity import Severity


class HandlerSettings:
    """Settings for logging to be applied to a specific Handler"""

    def __init__(
        self,
        severity: Severity | int | str = None,
        output_to_file: bool = None,
        use_color: bool = None,
        date_format: str = None,
        short_trace: bool = None,
        color_palette: int = None,
        inline_location: set[Severity] = None,
    ) -> None:
        if severity is not None and not isinstance(severity, Severity):
            severity = Severity(severity)
        self._severity = severity
        self._output_to_file = output_to_file
        self._use_color = use_color
        self._short_trace = short_trace
        self._inline_location = inline_location
        self._date_format = date_format
        self._color_palette = color_palette
        self._lock = threading.Lock()

    @property
    def severity(self) -> Severity:
        if self._severity is None:
            return logger_globals.severity
        return self._severity

    @severity.setter
    def severity(self, value: Severity | int | str):
        if not isinstance(value, Severity):
            value = Severity(value)
        with self._lock:
            self._severity = value

    @property
    def color_palette(self) -> int:
        if self._color_palette is None:
            return logger_globals.color_palette
        return self._color_palette

    @color_palette.setter
    def color_palette(self, value: int) -> None:
        with self._lock:
            self._color_palette = value

    @property
    def date_format(self) -> str:
        if self._date_format is None:
            return logger_globals.date_format
        return self._date_format

    @date_format.setter
    def date_format(self, value: str) -> None:
        with self._lock:
            self._date_format = value

    @property
    def output_to_file(self) -> bool:
        if self._output_to_file is None:
            return logger_globals.output_to_file
        return self._output_to_file

    @output_to_file.setter
    def output_to_file(self, value: bool):
        with self._lock:
            self._output_to_file = value

    @property
    def use_color(self) -> bool:
        if self._use_color is None:
            return logger_globals.use_color
        return self._use_color

    @use_color.setter
    def use_color(self, value: bool):
        with self._lock:
            self._use_color = value

    @property
    def short_trace(self) -> bool:
        if self._short_trace is None:
            return logger_globals.short_trace
        return self._short_trace

    @short_trace.setter
    def short_trace(self, value: bool):
        with self._lock:
            self._short_trace = value

    @property
    def inline_location(self) -> set:
        if self._inline_location is None:
            return logger_globals.inline_location
        return self._inline_location
