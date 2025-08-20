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

# Subject - keeps all information about the logged thing

import asyncio
import datetime
import inspect
import multiprocessing
import threading
from collections.abc import MutableMapping
from types import FrameType, TracebackType
from typing import NamedTuple, Any, Iterator
from .severity import Severity

# from .topic import extract_topic

__all__ = [
    "Subject",
    "SourceExtractLine",
    "FrameInformation",
    "TracebackRecord",
    "get_frame_information",
    "get_traceback_information",
    "get_source_location",
]

from .topic import Topic


class SourceExtractLine(NamedTuple):
    number: int
    """Line number in source file."""
    line: str
    """Line in source file."""


class FrameInformation(NamedTuple):
    source: list[SourceExtractLine] = [].copy()
    """List of :class:`hakisto.SourceExtractLine`."""
    local_vars: dict[str, str] = {}.copy()
    """The local variables as a dictionary with the values being converted to strings."""


class TracebackRecord(NamedTuple):
    source_location: str
    """.. include:: source_location.txt"""
    frame_information: FrameInformation
    """see :class:`hakisto.FrameInformation`."""


def get_frame_information(frame: FrameType) -> FrameInformation:
    """Extract source and local variables from a frame.

    :param frame: Frame object.
    :type frame: :class:`types.FrameType`
    :return: Source and local variables.
    :rtype: :class:`hakisto.FrameInformation`
    """
    try:
        lines, first_line_number = inspect.getsourcelines(frame)
    except OSError:  # pragma: no cover
        return FrameInformation()
    if not first_line_number:  # pragma: no cover
        first_line_number = 1  # for <module> the whole source is returned,
        lines = lines[: frame.f_lineno]  # but the line numbers are wrong
    return FrameInformation(
        [
            SourceExtractLine(n + first_line_number, line.rstrip())
            for n, line in enumerate(lines)
        ],
        {
            k: str(frame.f_locals[k])
            for k in sorted(frame.f_locals)
            if not k.startswith("__")
        },
    )


def get_traceback_information(frame: TracebackType) -> list[TracebackRecord]:
    """Return the traceback items, each having source location, source extract, and local variables"""
    result = []
    while frame:
        result.append(
            TracebackRecord(
                get_source_location(frame.tb_frame),
                get_frame_information(frame.tb_frame),
            )
        )
        frame = frame.tb_next
    return result


def get_source_location(frame: FrameType) -> str:
    """.. include:: source_location.txt"""
    try:
        return f'File "{frame.f_code.co_filename}", line {frame.f_lineno} in {frame.f_code.co_name}'
    except AttributeError:
        return ""


def get_inline_location(frame: FrameType) -> str:
    try:
        return f"{frame.f_code.co_name}:{frame.f_lineno}"
    except AttributeError:
        return ""


class Subject(MutableMapping):
    """The Subject represents the information that is being logged.

    :param topic: The topic of the subject. A possible root indicator will be removed.
    :param severity: The severity of the entry. A Handler uses the severity to determine if an entry should be made in the respective log.
    :type severity: int
    :param frame: The frame (of the call-stack) that issued the entry. For an Exception this contains the Traceback.
    :type frame: :class:`FrameType`
    :param message: The message of the entry.
    :type message: Optional[str]
    :param message_id: The message id.
    :type message_id: Optional[str]
    :param force_location: Force output of location
    :type force_location: bool

    Any additional keyword arguments will be available as mapping items.
    """

    severity: Severity
    """This should be one of the severities below.
    
    .. include:: severities_table.txt
    """
    created: datetime.datetime
    """The **UTC** date and time when the logging subject was created."""
    message_id: str
    """Message id, possible coming from a different system that uses these to identify the message reason."""
    thread_name: str
    thread_id: int
    process_name: str
    process_id: int
    asyncio_task_name: str
    message: str

    frame: FrameType | TracebackType
    """The execution frame that issued the entry. 
    Used to determine additional (beneficial) information (see items below).
    If the Subject is created be the Automatic Exception Handling, it points to the respective **Traceback**."""

    def __init__(
        self,
        severity: Severity,
        topic: Topic = None,
        frame: FrameType | TracebackType | None = None,
        message: str = None,
        message_id: str = None,
        force_location: bool = False,
        **kwargs,
    ) -> None:
        self.topic = topic or Topic()
        self.severity = severity
        self.created = datetime.datetime.now(datetime.UTC)
        self.message_id = message_id
        self.force_location = force_location
        self.message = message
        self.frame = frame

        self.__data = kwargs.copy()
        self.__cache = {}

        self.thread_name = threading.current_thread().name
        self.thread_id = threading.current_thread().ident
        self.process_name = multiprocessing.current_process().name
        self.process_id = multiprocessing.current_process().ident
        try:
            self.asyncio_task_name = asyncio.current_task().get_name()
        except RuntimeError:
            self.asyncio_task_name = ""

    @property
    def source_location(self) -> str:
        """.. include:: source_location.txt"""
        return get_source_location(self.frame)

    @property
    def inline_location(self) -> str:
        """Inline location for identifier"""
        return get_inline_location(self.frame)

    @property
    def source(self) -> list[SourceExtractLine]:
        """Source extract related to the entry."""
        self.__cache_source_and_local_vars()
        return self.__cache["source"]

    @property
    def local_vars(self) -> dict[str, str]:
        """Local variables related to the entry."""
        self.__cache_source_and_local_vars()
        return self.__cache["local_vars"]

    @property
    def traceback(self) -> list[TracebackRecord]:
        """List of traceback items to the entry."""
        if "traceback" not in self.__cache:
            if isinstance(self.frame, TracebackType):
                self.__cache["traceback"] = get_traceback_information(self.frame)
            else:
                self.__cache["traceback"] = []
        return self.__cache["traceback"]

    def __cache_source_and_local_vars(self) -> None:
        if "source" not in self.__cache:
            if isinstance(self.frame, FrameType):
                (self.__cache["source"], self.__cache["local_vars"]) = (
                    get_frame_information(self.frame)
                )
            else:
                self.__cache["source"], self.__cache["local_vars"] = [], {}

    def __setitem__(self, key, value, /):
        self.__data[key] = value

    def __delitem__(self, key, /):
        del self.__data[key]

    def __getitem__(self, key, /) -> Any:
        return self.__data[key]

    def __len__(self) -> int:
        return len(self.__data)

    def __iter__(self) -> Iterator[str]:
        return iter(self.__data)

    def __str__(self) -> str:
        return (
            f"{self.severity}, "
            f"{self.created}, "
            f"{self.message_id}, "
            f"{self.force_location}, "
            f"{self.thread_name}, "
            f"{self.thread_id}, "
            f"{self.process_name}, "
            f"{self.process_id}, "
            f"{self.asyncio_task_name}, "
            f"{self.topic}, "
            f"{self.message}, "
            f"{self.source_location}, "
            f"{self.__data}"
        )
