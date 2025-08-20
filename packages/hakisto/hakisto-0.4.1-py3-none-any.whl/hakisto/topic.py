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

from typing import Iterable

__all__ = ["Topic"]


class Topic(tuple):
    """A Topic describes the location withing the logging hierarchy.

    The top level is the empty topic.

    Separator is ``/``. Leading and trailing whitespace is removed for each component.
    Components are forced to be strings.

    A Topic is considered to contain OTHER Topic, if all elements of topic are in OTHER (starting at the first).
    """

    def __new__(cls, topic: str | Iterable[str] = ""):
        if isinstance(topic, str):
            topic = topic.split("/")
        topic = [str(i).strip() for i in topic]
        return super().__new__(cls, tuple([i for i in topic if i]))

    def __contains__(self, other: "Topic") -> bool:
        if not len(self):
            # The empty Topic is the root and contains every other Topic
            return True
        if len(self) > len(other):
            # Topic has more elements, therefore other CANNOT be in Topic
            return False
        return all([i == j for i, j in zip(self, other)])

    def __str__(self):
        return "/".join(self)

    def __eq__(self, other):
        return str(self) == str(other)
