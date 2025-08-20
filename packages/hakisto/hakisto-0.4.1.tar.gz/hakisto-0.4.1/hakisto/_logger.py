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


import inspect
import sys
from types import FrameType, TracebackType


from ._base import _LoggerHandlerBase
from ._logger_globals import logger_globals

from .severity import (
    TRACE,
    DEBUG,
    VERBOSE,
    INFO,
    SUCCESS,
    WARNING,
    ERROR,
    CRITICAL,
    Severity,
)
from .subject import Subject


__all__ = ["Logger"]


class Logger(_LoggerHandlerBase):
    """Main Logger class. Can be inherited from, but should be sufficient for most situations.

    """

    def critical(
        self, *args: str, message_id: str = None, force_location: bool = False, **kwargs
    ) -> None:
        """Log a **CRITICAL** entry.

        ``CRITICAL`` entries will include the respective source location, source section and local variables.

        :param args: The Message(s). Every message will create a separate entry.
        :param message_id: Message ID.
        :param force_location: Force output of location
        """
        self.log(
            CRITICAL,
            message_id=message_id,
            force_location=force_location,
            *args,
            **kwargs,
        )

    def error(
        self, *args: str, message_id: str = None, force_location: bool = False, **kwargs
    ) -> None:
        """Log an **ERROR** entry.

        ``ERROR`` entries will include the respective source location.

        :param args: The Message(s). Every message will create a separate entry.
        :param message_id: Message ID.
        :param force_location: Force output of location
        """
        self.log(
            ERROR, message_id=message_id, force_location=force_location, *args, **kwargs
        )

    def warning(
        self, *args: str, message_id: str = None, force_location: bool = False, **kwargs
    ) -> None:
        """Log a **WARNING** entry.

        :param args: The Message(s). Every message will create a separate entry.
        :param message_id: Message ID.
        :param force_location: Force output of location
        """
        self.log(
            WARNING,
            message_id=message_id,
            force_location=force_location,
            *args,
            **kwargs,
        )

    def success(
        self, *args: str, message_id: str = None, force_location: bool = False, **kwargs
    ) -> None:
        """Log a **SUCCESS** entry.

        This has been added to support responses from SAP.

        :param args: The Message(s). Every message will create a separate entry.
        :param message_id: Message ID.
        :param force_location: Force output of location
        """
        self.log(
            SUCCESS,
            message_id=message_id,
            force_location=force_location,
            *args,
            **kwargs,
        )

    def info(
        self, *args: str, message_id: str = None, force_location: bool = False, **kwargs
    ) -> None:
        """Log an **INFO** entry.

        :param args: The Message(s). Every message will create a separate entry.
        :param message_id: Message ID.
        :param force_location: Force output of location
        """
        self.log(
            INFO, message_id=message_id, force_location=force_location, *args, **kwargs
        )

    def verbose(
        self, *args: str, message_id: str = None, force_location: bool = False, **kwargs
    ) -> None:
        """Log a **VERBOSE** entry.

        :param args: The Message(s). Every message will create a separate entry.
        :param message_id: Message ID.
        :param force_location: Force output of location
        """
        self.log(
            VERBOSE,
            message_id=message_id,
            force_location=force_location,
            *args,
            **kwargs,
        )

    def debug(
        self, *args: str, message_id: str = None, force_location: bool = False, **kwargs
    ) -> None:
        """Log a **DEBUG** entry.

        :param args: The Message(s). Every message will create a separate entry.
        :param message_id: Message ID.
        :param force_location: Force output of location
        """
        self.log(
            DEBUG, message_id=message_id, force_location=force_location, *args, **kwargs
        )

    def trace(
        self, *args: str, message_id: str = None, force_location: bool = False, **kwargs
    ) -> None:
        """Log a **TRACE** entry.

        :param args: The Message(s). Every message will create a separate entry.
        :param message_id: Message ID.
        :param force_location: Force output of location
        """
        self.log(
            TRACE, message_id=message_id, force_location=force_location, *args, **kwargs
        )

    def log(
        self,
        severity,
        *args: str,
        message_id: str = None,
        force_location: bool = False,
        **kwargs,
    ) -> None:
        """Log an entry.

        While this method has been made public, be advised, that using integers directly might break in the
        future, if the implementation is modified.

        :param severity: The severity level of the log entry.
        :param args: The Message(s). Every message will create a separate entry.
        :param message_id: Message ID.
        :param force_location: Force output of location
        """
        if not all((self._is_active, self.settings.severity <= severity)):
            return

        frame = self._get_caller()
        for message in args:
            subject = Subject(
                topic=self._topic,
                severity=severity,
                frame=frame,
                message=str(message),
                message_id=message_id,
                force_location=force_location,
                **kwargs,
            )
            for handler in logger_globals.handlers:
                # noinspection PyBroadException
                try:
                    handler(subject)
                except:
                    pass

    @staticmethod
    def _get_caller() -> FrameType:
        """Return *real* caller.

        If this method is overridden, make sure that the right frames are excluded.

        :meta public:
        """
        frame = inspect.currentframe()
        while frame.f_code.co_filename in logger_globals.excluded_source_files:
            frame = frame.f_back
        return frame

    def __repr__(self):
        return f"Logger({self._topic})"


def log_exception(exception_class, exception: Exception, trace_back: TracebackType):
    """Hook to handle uncaught exceptions.

    The entry is sent to **all** Handlers.

    A :class:`imuthes.logging.Handler` **must** implement ``handle_exception`` when it should react to this.

    :param exception_class: Not used
    :type exception_class: object
    :param exception:
    :param trace_back:
    """
    subject = Subject(
        severity=Severity(sys.maxsize), frame=trace_back, message=f'{exception_class.__name__}: {exception}',
    )
    for handler in logger_globals.handlers:
        # noinspection PyBroadException
        try:
            handler.handle_exception(subject)
        except:
            pass


logger_globals.register_excluded_source_file(inspect.currentframe().f_code.co_filename)
sys.excepthook = log_exception
