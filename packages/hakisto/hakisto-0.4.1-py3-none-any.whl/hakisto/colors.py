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

# ANSI colors for console output

# fmt: off
BLACK         = '\033[30m'
RED           = '\033[31m'
GREEN         = '\033[32m'
YELLOW        = '\033[33m'
BLUE          = '\033[34m'
MAGENTA       = '\033[35m'
CYAN          = '\033[36m'
WHITE         = '\033[37m'

LIGHT_BLACK   = '\033[90m'
LIGHT_RED     = '\033[91m'
LIGHT_GREEN   = '\033[92m'
LIGHT_YELLOW  = '\033[93m'
LIGHT_BLUE    = '\033[94m'
LIGHT_MAGENTA = '\033[95m'
LIGHT_CYAN    = '\033[96m'
LIGHT_WHITE   = '\033[97m'

RESET         = '\033[39m'
# fmt: on

__all__ = [
    "BLACK",
    "RED",
    "GREEN",
    "YELLOW",
    "BLUE",
    "MAGENTA",
    "CYAN",
    "WHITE",
    "LIGHT_BLACK",
    "LIGHT_RED",
    "LIGHT_GREEN",
    "LIGHT_YELLOW",
    "LIGHT_BLUE",
    "LIGHT_MAGENTA",
    "LIGHT_CYAN",
    "LIGHT_WHITE",
    "RESET",
    "colorize_string",
]


def colorize_string(value: str, color: str = "") -> str:
    """Return colorized string when a color is provided.

    :param value: The string to colorize.
    :type value: str
    :param color: The color, should be the complete ANSI escape code (see :doc:`colors`).
    :type color: Optional[str]
    :return: The colorized string
    :rtype: str
    """
    if color:
        return f"{color}{value}{RESET}"
    return value
