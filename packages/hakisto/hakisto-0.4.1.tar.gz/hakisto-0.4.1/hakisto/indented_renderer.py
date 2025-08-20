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

from .handler import Identifier
from .colors import colorize_string

__all__ = ["IndentedRenderer"]


class IndentedRenderer:
    """Mixin using the second part of :class:`hakisto.Identifier` to indent lines and provide readable output.

    .. Warning:: Inherit **before** Handler.
    """

    @staticmethod
    def render(identifier: Identifier, content: str, color: str = "") -> str:
        """Render the provided content for output.

        :param identifier: The identifier that will be used.
        :type identifier: :class:`Identifier`
        :param content: The content to be rendered. Might contain new-line(s).
        :type content: str
        :param color: The color of the content if applicable.
        :type content: str
        :return: The rendered content.
        :rtype: str
        """
        if "\n" in content:
            content = f"\n{colorize_string(identifier.continuation, color)} ".join(
                content.split("\n")
            )
        return f"{colorize_string(identifier.identifier, color)} {content}"
