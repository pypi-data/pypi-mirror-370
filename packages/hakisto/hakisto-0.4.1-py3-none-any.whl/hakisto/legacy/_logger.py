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
import collections
import warnings
from logging import Logger as BaseLogger, NOTSET
from types import MappingProxyType

from .._logger import Logger

## more work to be done not even alpha!

# fmt: off
level_to_severity = MappingProxyType({
     0:   0,
    10: 200,
    20: 400,
    30: 600,
    40: 800,
    50: 900,
})
# fmt: on


class LegacyLogger(BaseLogger):
    """Drop-in replacement of ``logging.Logger`` to support handling messages from existing libraries.

    Provides the same interface as ``logging.Logger`` but behaves like :class:`hakisto.Logger`.

    Use ``logging.setLoggerClass()`` to enable.

    .. code:: python

       from logging import setLoggerClass
       from hakisto.legacy import LegacyLogger

       setLoggerClass(LegacyLogger)

    or

    .. code:: python

       from hakisto.legacy import enable_legacy_logger

       enable_legacy_logger()
    """

    def __init__(self, name: str, level: int = NOTSET):
        super(LegacyLogger, self).__init__(name, level)
        self._logger = Logger(name)

    def setLevel(self, level):
        """
        Set the logging level of this logger.  level must be an int or a str.
        """
        super(LegacyLogger, self).setLevel(level)
        self._logger.set_severity(level_to_severity.get(self.level, 0))

    @staticmethod
    def _convert_legacy_message(msg, args) -> str:
        if all(
            (
                args,
                len(args) == 1,
                isinstance(args[0], collections.abc.Mapping),
                args[0],
            )
        ):
            args = args[0]
        args = args
        if args:
            msg = str(msg) % args
        return msg

    def debug(self, msg, *args, **kwargs):
        """
        Log 'msg % args' with severity 'DEBUG'.

        To pass exception information, use the keyword argument exc_info with
        a true value, e.g.

        logger.debug("Houston, we have a %s", "thorny problem", exc_info=1)
        """
        self._logger.debug(self._convert_legacy_message(msg, args), **kwargs)

    def info(self, msg, *args, **kwargs):
        """
        Log 'msg % args' with severity 'INFO'.

        To pass exception information, use the keyword argument exc_info with
        a true value, e.g.

        logger.info("Houston, we have a %s", "notable problem", exc_info=1)
        """
        self._logger.info(self._convert_legacy_message(msg, args), **kwargs)

    def warning(self, msg, *args, **kwargs):
        """
        Log 'msg % args' with severity 'WARNING'.

        To pass exception information, use the keyword argument exc_info with
        a true value, e.g.

        logger.warning("Houston, we have a %s", "bit of a problem", exc_info=1)
        """
        self._logger.warning(self._convert_legacy_message(msg, args), **kwargs)

    def warn(self, msg, *args, **kwargs):
        warnings.warn(
            "The 'warn' method is deprecated, use 'warning' instead",
            DeprecationWarning,
            2,
        )
        self._logger.warning(self._convert_legacy_message(msg, args), **kwargs)

    def error(self, msg, *args, **kwargs):
        """
        Log 'msg % args' with severity 'ERROR'.

        To pass exception information, use the keyword argument exc_info with
        a true value, e.g.

        logger.error("Houston, we have a %s", "major problem", exc_info=1)
        """
        self._logger.error(self._convert_legacy_message(msg, args), **kwargs)

    def exception(self, msg, *args, exc_info=True, **kwargs):
        """
        Convenience method for logging an ERROR with exception information.
        """
        self._logger.critical(self._convert_legacy_message(msg, args), **kwargs)

    def critical(self, msg, *args, **kwargs):
        """
        Log 'msg % args' with severity 'CRITICAL'.

        To pass exception information, use the keyword argument exc_info with
        a true value, e.g.

        logger.critical("Houston, we have a %s", "major disaster", exc_info=1)
        """
        self._logger.critical(self._convert_legacy_message(msg, args), **kwargs)

    def fatal(self, msg, *args, **kwargs):
        """
        Don't use this method, use critical() instead.
        """
        self._logger.critical(self._convert_legacy_message(msg, args), **kwargs)

    def log(self, level, msg, *args, **kwargs):
        """
        Log 'msg % args' with the integer severity 'level'.

        To pass exception information, use the keyword argument exc_info with
        a true value, e.g.

        logger.log(level, "We have a %s", "mysterious problem", exc_info=1)
        """
        self._logger.log(
            level_to_severity.get(level, 0),
            self._convert_legacy_message(msg, args),
            **kwargs
        )
