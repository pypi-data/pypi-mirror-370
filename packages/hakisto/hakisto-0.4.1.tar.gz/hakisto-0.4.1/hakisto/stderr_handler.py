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


from .indented_renderer import IndentedRenderer
from .handler import Handler
from .stream import Stream

__all__ = ["StdErrHandler"]


class StdErrHandler(IndentedRenderer, Handler):
    """Color Output to console

    :param name: Handler name (used to determine topic)
    :type name: str
    :param colors: Color palette to use
    :type colors: dict[int, str]
    """

    def __init__(self, name: str = "", colors: dict[int, str] = None, **kwargs):
        super().__init__(name, **kwargs)
        self.stream = Stream("<stderr>")

    def write(self, content: str) -> None:
        """Write content to console"""
        with self.stream:
            self.stream.write(f"{content}\n")
