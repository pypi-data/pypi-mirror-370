import os
from typing import Type, Any, Callable

import click

from ._click import FC, make_decorator
from .._logger import Logger


def hakisto_use_color(
    *param_decls: str,
    default: bool = None,
    show_default: bool = True,
    cls: Type[click] | None = None,
    **attrs: Any
) -> Callable[[FC], FC]:
    """Attaches option to use short trace (source list for last only).

    This is a boolean option, with the default provided, taken from HAKISTO_USE_COLOR or ``True``.

    All positional arguments are  passed as parameter declarations to :class:`Option`,
    if none are provided, defaults to ``--log-short-trace/--no-log-short-trace``.

    Keyword arguments not described below are passed as keyword arguments to :func:`click.Option`,
    arguments are forwarded unchanged (except ``cls``).

    :param default:
    :param show_default:
    :param cls: the option class to instantiate.  This defaults to :class:`Option`.
    :param param_decls: Passed as positional arguments to the constructor of ``cls``.
    :param attrs: Passed as keyword arguments to the constructor of ``cls``.
    """

    attrs["default"] = default if default is not None else os.getenv("HAKISTO_USE_COLOR", "TRUE").upper() in (
        "TRUE",
        "ON",
        "1",
        "YES",
    )
    attrs["show_default"] = show_default
    attrs["help"] = attrs.get("help", "Use color?")

    return make_decorator(
        cls=cls or click.Option,
        param_decls=param_decls or ("--log-use-color/--no-log-use-color",),
        **attrs
    )


def hakisto_process_use_color(log_use_color: bool, **kwargs) -> None:
    """Process the Hakisto use color option.

    :param log_use_color:
    """
    Logger.global_use_color = log_use_color
