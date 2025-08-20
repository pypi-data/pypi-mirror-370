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

import datetime
import pathlib
from types import MappingProxyType

from .indented_renderer import IndentedRenderer
from .handler import Handler
from .stream import Stream

KILOBYTE = 1024
MEGABYTE = KILOBYTE * 1024
GIGABYTE = MEGABYTE * 1024

SIZE_FACTORS = MappingProxyType(dict(k=KILOBYTE, m=MEGABYTE, g=GIGABYTE))

__all__ = ["FileHandler", "rotate_file"]


def rotate_file(path: pathlib.Path, generations: int = 0) -> None:
    """'Rotates' a file, i.e. creates a backup while limiting the number of backups kept.

    The backup file are named depending on the value of ``generation``.

    Given a name of ``main.log`` the following applies.

    .. list-table::
       :header-rows: 1

       * - Condition
         - Result
         - Example
       * - value > 99
         - main.<nnn>.log
         - main.001.log
       * - 10 <= value < 100
         - main.<nn>.log
         - main.01.log
       * - 1 <= value < 10
         - main.<n>.log
         - main.1.log
       * - value = 0
         - main.<log>.bak
         - main.log.bak
       * - value < 0
         - main.<date_time>.log
         - main.060102_220405.log

    where ``date_time`` is formatted as ``yymmdd_hhmmss``.

    :param path: The path of the file to be rotated
    :type path: pathlib.Path
    :param generations: The maximum number of generations to be kept

    :param path:
    :param generations:
    """
    suffix = path.suffix

    if not generations:
        if path.exists():
            path.replace(path.with_suffix(f"{suffix}.bak"))
        return

    if generations > 0:
        num_length = len(str(generations))
        for generation in reversed(range(generations)):
            temp_path = (
                path.with_suffix(f".{generation:0{num_length}}{suffix}")
                if generation
                else path
            )
            if temp_path.exists():
                temp_path.replace(
                    path.with_suffix(f".{generation + 1:0{num_length}}{suffix}")
                )
        return

    # when generations is negative, find all backup files
    backup_files = sorted(
        path.parent.glob(
            f"{path.stem}.[0-9][0-9][0-9][0-9][0-9][0-9]_[0-9][0-9][0-9][0-9][0-9][0-9]{suffix}"
        )
    )
    while len(backup_files) >= -generations:
        backup_files.pop(0).unlink()
    path.replace(
        path.with_suffix(
            f".{datetime.datetime.now(datetime.UTC).strftime('%y%m%d_%H%M%S')}{suffix}"
        )
    )


class FileHandler(IndentedRenderer, Handler):
    """Output to a log file.

    :param name: Handler name (used to determine topic)
    :type name: str
    :param path: Log file to use
    :type path: :class:`pathlib.Path` or str
    :param max_size: Size when file will be rotated
    :type max_size: int or str
    :param generations: Maximum Number of generations. Negative numbers use DATE_TIME instead of numbers in the file name.
    :type generations: int
    """

    def __init__(
        self,
        name: str = "",
        path: pathlib.Path | str = None,
        max_size: int | str = "2m",
        generations: int = 10,
        **kwargs,
    ):
        super().__init__(name, **kwargs)
        self.stream = Stream(path)
        if isinstance(max_size, str):
            if not max_size.isdigit():
                factor = SIZE_FACTORS[max_size[-1].lower()]
                max_size = int(max_size[:-1]) * factor
            else:
                max_size = int(max_size)
        self.max_size = max_size
        self.generations = generations

    def get_color(self, severity) -> str:
        return ""

    def write(self, content: str) -> None:
        """Write content to file, check if rollover is required first."""
        with self.stream:
            self.stream.write(f"{content}\n")

    def is_rollover_required(self, content) -> bool:
        try:
            return all(
                (
                    self.max_size,
                    ((self.stream.path.stat().st_size + len(content)) > self.max_size),
                )
            )
        except FileNotFoundError:
            return False
