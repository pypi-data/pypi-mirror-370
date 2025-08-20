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

#  Handlers (listeners) are attached using pypubsub, but we want to isolate this
#  from other usages.

from types import MappingProxyType

from .colors import (
    LIGHT_MAGENTA,
    LIGHT_CYAN,
    LIGHT_GREEN,
    LIGHT_YELLOW,
    LIGHT_RED,
    MAGENTA,
    CYAN,
    GREEN,
    YELLOW,
    RED,
)

__all__ = [
    "TRACE",
    "DEBUG",
    "VERBOSE",
    "INFO",
    "SUCCESS",
    "WARNING",
    "ERROR",
    "CRITICAL",
    "Severity",
]

_T = 100
_D = 200
_V = 300
_I = 400
_S = 500
_W = 600
_E = 700
_C = 800


class Severity(int):
    values = MappingProxyType(
        {
            0: "NOTSET",
            _T: "TRACE",
            _D: "DEBUG",
            _V: "VERBOSE",
            _I: "INFO",
            _S: "SUCCESS",
            _W: "WARNING",
            _E: "ERROR",
            _C: "CRITICAL",
        }
    )
    names = MappingProxyType({v: k for k, v in values.items()})
    colors = MappingProxyType(
        {
            _T: (LIGHT_MAGENTA, MAGENTA),
            _D: (LIGHT_CYAN, CYAN),
            _V: (LIGHT_GREEN, GREEN),
            _I: (LIGHT_GREEN, GREEN),
            _S: (LIGHT_GREEN, GREEN),
            _W: (LIGHT_YELLOW, YELLOW),
            _E: (LIGHT_RED, RED),
            _C: (LIGHT_RED, RED),
        }
    )

    def __new__(cls, value):
        if not isinstance(value, int):
            if value.upper() not in cls.names:
                raise ValueError(f"{value} is not a valid severity name")
            value = cls.names[value.upper()]
        return super().__new__(cls, value)

    def __str__(self):
        return self.values.get(self, super().__str__())

    def color(self, palette: int = 0) -> str:
        """Get respective color from palette"""
        i = min(self // 100, 8) * 100
        if not i:
            return ""
        return self.colors[i][palette]


# fmt: off
TRACE    = Severity(_T)  # More information than regular DEBUG (e.g. variable values).
DEBUG    = Severity(_D)  # Debugging (technical) information.
VERBOSE  = Severity(_V)  # Additional (non-technical) information.
INFO     = Severity(_I)  # Information.
SUCCESS  = Severity(_S)  # Successful execution.
WARNING  = Severity(_W)  # Warning that might require attention.
ERROR    = Severity(_E)  # Significant issue. Processing might continue.
CRITICAL = Severity(_C)  # Critical issue. Usually processing is aborted.
# fmt: on
