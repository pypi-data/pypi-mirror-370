import typing

import click

# noinspection PyProtectedMember
from click.decorators import _param_memo

if typing.TYPE_CHECKING:
    import typing_extensions

    P = typing_extensions.ParamSpec("P")

R = typing.TypeVar("R")
T = typing.TypeVar("T")
_AnyCallable = typing.Callable[..., typing.Any]
FC = typing.TypeVar("FC", bound=typing.Union[_AnyCallable, click.Command])


def make_decorator(cls, param_decls, **attrs):

    def decorator(f: FC) -> FC:
        _param_memo(f, cls(param_decls, **attrs))
        return f

    return decorator
