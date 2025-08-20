import os
from typing import Type, Any, Callable

import click

from ._click import FC, make_decorator
from .._logger_globals import logger_globals


def hakisto_file(
    *param_decls: str,
    default: bool = None,
    show_default: bool = True,
    cls: Type[click] | None = None,
    **attrs: Any
) -> Callable[[FC], FC]:
    """Attaches option enable or disable logging to a file to the command.


    This is a boolean option, with the default provided, taken from HAKISTO_ENABLE_FILE or ``True``.

    All positional arguments are  passed as parameter declarations to :class:`Option`,
    if none are provided, defaults to ``--log-file/--no-log-file``.

    Keyword arguments not described below are passed as keyword arguments to :func:`click.Option`,
    arguments are forwarded unchanged (except ``cls``).

    :param default:
    :param show_default:
    :param cls: the option class to instantiate.  This defaults to :class:`Option`.
    :param param_decls: Passed as positional arguments to the constructor of ``cls``.
    :param attrs: Passed as keyword arguments to the constructor of ``cls``.
    """
    attrs["default"] = default if default is not None else os.getenv("HAKISTO_ENABLE_FILE", "True").upper() in (
        "TRUE",
        "ON",
        "1",
        "YES",
    )
    attrs["show_default"] = show_default
    attrs["help"] = attrs.get("help", "Log to file?")

    return make_decorator(
        cls=cls or click.Option,
        param_decls=param_decls or ("--log-file/--no-log-file",),
        **attrs
    )


def hakisto_process_file(log_file: bool, **kwargs) -> None:
    """Process the Hakisto File option.

    :param log_file:
    :type log_file: bool
    """
    logger_globals.output_to_file = log_file
