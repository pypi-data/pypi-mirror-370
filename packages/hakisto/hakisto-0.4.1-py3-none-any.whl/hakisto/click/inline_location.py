from typing import Callable, Any, Type, Sequence

import click

from ._click import FC, make_decorator
from ..severity import Severity
from .._logger_globals import logger_globals


def hakisto_inline_location(
    *param_decls: str,
    choices: Sequence[str] = None,
    case_sensitive: bool = False,
    cls: Type[click.Option] | None = None,
    **attrs: Any,
) -> Callable[[FC], FC]:
    """Attaches option to include the location in the identifier (will not be clickable), for the respective
    Severity. Can be used multiple times.

    All positional arguments are  passed as parameter declarations to :class:`Option`,
    if none are provided, defaults to ``--log-inline-location``.

    Keyword arguments not described below are passed as keyword arguments to :func:`click.Option`,
    arguments are forwarded unchanged (except ``cls``).

    :param choices: List of permitted Hakisto Severities.
    :param case_sensitive:
    :param cls: the option class to instantiate.  This defaults to :class:`Option`.
    :param param_decls: Passed as positional arguments to the constructor of ``cls``.
    :param attrs: Passed as keyword arguments to the constructor of ``cls``.
    """

    attrs["multiple"] = True
    if not choices:
        choices = list(Severity.names.keys())
        choices.append("ALL")
    choices = [i.upper() for i in choices]
    attrs["type"] = click.Choice(choices, case_sensitive=case_sensitive)
    attrs["help"] = attrs.get("help", "Show file location inline for severity")

    return make_decorator(
        cls=cls or click.Option,
        param_decls=param_decls or ("--log-inline-location",),
        **attrs,
    )


def hakisto_process_inline_location(log_inline_location: tuple, **kwargs) -> None:
    """Process the Hakisto show location option."""

    if "ALL" in log_inline_location:
        for k in Severity.values:
            if k:
                logger_globals.inline_location.add(Severity(k))

    else:
        for i in log_inline_location:
            logger_globals.inline_location.add(Severity(i))
