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

# default logger (batteries included)

from ._logger import Logger as _Logger
from ._logger_globals import logger_globals
from .stderr_handler import StdErrHandler

_logger = _Logger()

critical = _logger.critical
error = _logger.error
warning = _logger.warning
success = _logger.success
info = _logger.info
verbose = _logger.verbose
debug = _logger.debug
trace = _logger.trace
log = _logger.log

logger_globals.add_handler(StdErrHandler())
# file_handler = FileHandler()
