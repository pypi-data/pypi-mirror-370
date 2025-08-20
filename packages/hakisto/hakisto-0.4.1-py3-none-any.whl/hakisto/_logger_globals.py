#  hakisto - logging reimagined
#
#  Copyright (C) 2024  Bernhard Radermacher
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Lesser General Public License as published
#  by the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.

import os
import threading


from .severity import Severity


class LoggerGlobals:
    """Singleton to store global information for logging"""

    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(LoggerGlobals, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        self._severity = Severity(
            os.getenv("HAKISTO_SEVERITY", "").strip().upper() or 0
        )
        self._output_to_file = os.getenv(
            "HAKISTO_ENABLE_FILE", "True"
        ).strip().upper() in ("TRUE", "ON", "1", "YES")
        self._use_color = os.getenv("HAKISTO_USE_COLOR", "True").strip().upper() in (
            "TRUE",
            "ON",
            "1",
            "YES",
        )
        self._short_trace = os.getenv(
            "HAKISTO_SHORT_TRACE", "False"
        ).strip().upper() in ("TRUE", "ON", "1", "YES")
        hakisto_inline_location = set(
            [
                i.strip()
                for i in os.getenv("HAKISTO_INLINE_LOCATION", "").upper().split()
            ]
        )
        if "ALL" in hakisto_inline_location:
            hakisto_inline_location = set(
                [v for k, v in Severity.values.items() if k > 0]
            )
        self._inline_location = set([Severity(i) for i in hakisto_inline_location])
        self._date_format = os.getenv(
            "HAKISTO_SHORT_TRACE", "%y-%m-%d %H:%M:%S"
        ).strip()
        self._color_palette = {
            "LIGHT": 0,
            "DARK": 1,
        }.get(os.getenv("HAKISTO_COLORS", "").strip().upper(), 0)

        self._excluded_source_files = set()
        self._handlers = set()

    def register_excluded_source_file(self, file_name: str) -> None:
        """This must be called in the source file of any descendent to exclude the respective
        entries in the call-stack.

        Recommendation: Call on source file level (module).

        .. code:: python

           logger_globals.register_excluded_source_file(inspect.currentframe().f_code.co_filename)

        :param file_name: Source file name
        """
        with self._lock:
            self._excluded_source_files.add(file_name)

    @property
    def excluded_source_files(self) -> set[str]:
        """Get a copy of excluded_source_files when identifying *real* caller in call-stack."""
        return self._excluded_source_files.copy()

    @property
    def color_palette(self) -> int:
        return self._color_palette

    @color_palette.setter
    def color_palette(self, value: int) -> None:
        if value < 0 or value > 1:
            value = 0
        with self._lock:
            self._color_palette = value

    @property
    def date_format(self) -> str:
        return self._date_format

    @date_format.setter
    def date_format(self, value: str) -> None:
        with self._lock:
            self._date_format = value

    @property
    def severity(self) -> Severity:
        return self._severity

    @severity.setter
    def severity(self, value: Severity | int | str) -> None:
        if not isinstance(value, Severity):
            value = Severity(value)
        with self._lock:
            self._severity = value

    @property
    def output_to_file(self) -> bool:
        return self._output_to_file

    @output_to_file.setter
    def output_to_file(self, value: bool) -> None:
        with self._lock:
            self._output_to_file = value

    @property
    def use_color(self) -> bool:
        return self._use_color

    @use_color.setter
    def use_color(self, value: bool) -> None:
        with self._lock:
            self._use_color = value

    @property
    def short_trace(self) -> bool:
        return self._short_trace

    @short_trace.setter
    def short_trace(self, value: bool) -> None:
        with self._lock:
            self._short_trace = value

    @property
    def inline_location(self) -> set:
        return self._inline_location

    def add_handler(self, handler) -> None:
        with self._lock:
            self._handlers.add(handler)

    def drop_handler(self, handler) -> None:
        with self._lock:
            self._handlers.discard(handler)

    @property
    def handlers(self) -> set:
        return self._handlers


logger_globals = LoggerGlobals()
