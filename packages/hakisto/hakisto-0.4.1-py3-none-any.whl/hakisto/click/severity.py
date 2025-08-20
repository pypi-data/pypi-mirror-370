import os
from typing import Sequence, Type, Any, Callable

import click

from ._click import FC, make_decorator
from .._logger_globals import logger_globals
from ..severity import Severity


def hakisto_severity(
    *param_decls: str,
    default: str = None,
    choices: Sequence[str] = None,
    case_sensitive: bool = False,
    show_default: bool = True,
    cls: Type[click.Option] | None = None,
    **attrs: Any,
) -> Callable[[FC], FC]:
    """Attaches HAKISTO SEVERITY option to the command.

    This is always a ``click.Choice`` option, with the default taken from HAKISTO_SEVERITY or ``INFO``.

    The default options are the Hakisto Severities (not case-sensitive).

    All positional arguments are  passed as parameter declarations to :class:`Option`,
    if none are provided, defaults to ``--log, --log-severity``.

    Keyword arguments not described below are passed as keyword arguments to :func:`click.Option`,
    arguments are forwarded unchanged (except ``cls``).

    :param default: default Hakisto Severity.
    :param choices: List of permitted Hakisto Severities.
    :param case_sensitive:
    :param show_default:
    :param cls: the option class to instantiate.  This defaults to :class:`Option`.
    :param param_decls: Passed as positional arguments to the constructor of ``cls``.
    :param attrs: Passed as keyword arguments to the constructor of ``cls``.
    """
    attrs["default"] = (default or os.getenv("HAKISTO_SEVERITY", "INFO")).upper()
    attrs["show_default"] = show_default
    attrs["type"] = click.Choice(
        [i.upper() for i in choices or Severity.names.keys()], case_sensitive=case_sensitive
    )
    attrs["help"] = attrs.get("help", "Minimum Logging Severity")

    return make_decorator(
        cls=cls or click.Option,
        param_decls=param_decls or ("--log", "--log-severity", "log_severity"),
        **attrs,
    )


def hakisto_process_severity(log_severity: str, **kwargs) -> None:
    """Process the Hakisto Severity option.

    :param log_severity:
    """
    logger_globals.severity = log_severity
