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

# thread save Stream

import inspect
import pathlib
import sys
import threading

from types import FrameType

__all__ = ["Stream", "get_top_caller"]


def get_top_caller() -> FrameType:
    """Return the frame at top of stack, basically the called script."""
    frame = inspect.currentframe()
    while frame.f_back:
        frame = frame.f_back
    return frame


class Stream:
    """Thread save stream, a singleton per ``name`` to prevent intermixing of output when threading is used.

    - If the name is provided will be considered the file name (of the logfile), except
      - ``<stderr>`` will use **stderr**
      - ``<stdout>`` will use **stdout**

    - If the name is **not** provided, the name of the called script will be used (with the extension ``.log``).

    - If the name is **not** provided **and** an interactive session is used, the logfile is named ``__stdin__.log``

    :param name: Name of the stream (logfile)
    :type name: str
    """

    __cache = {}

    def __new__(cls, name: str, *args, **kwargs):
        if name in cls.__cache:
            return cls.__cache[name]
        return super().__new__(cls)

    def __init__(self, name: str, *args, **kwargs):
        self.name = name
        self._stream = None
        self._lock = threading.RLock()
        self._path = None
        if self.name in ("<stdout>", "<stderr>"):
            self.get_stream = lambda: getattr(sys, name[1:-1])
        else:
            if not self.name:
                self.name = get_top_caller().f_code.co_filename
                if self.name.startswith("<") and self.name.endswith(">"):
                    self._path = pathlib.Path.cwd().with_name(
                        f"__{self.name[1:-1].replace(' ', '_')}__.log"
                    )
                elif self.name.endswith("pydevconsole.py"):
                    self._path = pathlib.Path.cwd().with_name("__stdin__.log")
                else:
                    self._path = pathlib.Path(self.name).with_suffix(".log")
            else:
                self._path = pathlib.Path(self.name)
            self.get_stream = lambda: self.path.open(mode="a", encoding="utf-8")
        self.__cache[self.name] = self
        if self.name.startswith("<std"):
            self.name = ""

    @property
    def path(self) -> pathlib.Path:
        """The file path of the stream. Might be None."""
        return self._path

    @property
    def lock(self):
        """The treading lock. Can be used in a ``with`` statement."""
        return self._lock

    def __enter__(self):
        self._lock.acquire()
        self._stream = self.get_stream()
        return self._stream

    def __exit__(self, exc_type, exc_val, exc_tb):
        if hasattr(self._stream, "flush"):
            self._stream.flush()
        if self.name and hasattr(self._stream, "close"):
            self._stream.close()
        self._lock.release()

    def open(self):
        """Open the stream and return it."""
        if not self._stream:
            self._stream = self.get_stream()
        return self._stream

    def close(self):
        """Close the stream."""
        if self._stream:
            if all(
                (self.name, hasattr(self._stream, "close"), not self._stream.closed)
            ):
                with self._lock:
                    self._stream.close()
                    self._stream = None

    def flush(self):
        """Flush the stream."""
        if self._stream:
            with self._lock:
                self._stream.flush()

    def write(self, data):
        """Write to the stream."""
        if self._stream:
            with self._lock:
                self._stream.write(data)

    def __del__(self):
        self.close()
