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

from .handler_settings import HandlerSettings
from .topic import Topic


class _LoggerHandlerBase:
    """Common base for Logger and Handler"""

    def __init__(
            self,
            topic: Topic | str | Iterable[str] = "",
            settings: HandlerSettings = None,
            **kwargs,
    ) -> None:
        self._topic = Topic(topic)
        self.settings = settings or HandlerSettings()
        self._is_active = True

    @property
    def is_active(self) -> bool:
        return self._is_active

    def activate(self, active: bool = True) -> None:
        self._is_active = active

    def deactivate(self) -> None:
        self.activate(active=False)
