from __future__ import annotations

import asyncio
import functools
import os
import traceback
from typing import Any, Callable

import typer
from click import ClickException
from typer.models import CommandFunctionType

RECURVE_TEST_MODE = os.getenv("RECURVE_TEST_MODE", "false").lower() == "true"


class RecurveTyper(typer.Typer):
    """
    Wrapper for Typer to support async functions and handle errors.
    """

    def command(self, name: str | None = None, *args, **kwargs) -> Callable[[CommandFunctionType], CommandFunctionType]:
        def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
            fn = func
            if asyncio.iscoroutinefunction(func):

                @functools.wraps(func)
                def sync_wrapper(*inner_args: Any, **inner_kwargs: Any) -> Any:
                    asyncio.run(func(*inner_args, **inner_kwargs))

                fn = sync_wrapper

            fn = with_cli_exception_handling(fn)

            return super(RecurveTyper, self).command(name=name, *args, **kwargs)(fn)

        return decorator


def exit_with_error(message: str, code: int = 1, **kwargs) -> None:
    """
    Utility to print a stylized error message and exit with a non-zero code
    """
    kwargs.setdefault("fg", typer.colors.RED)
    typer.secho(message, **kwargs)
    raise typer.Exit(code)


def with_cli_exception_handling(fn):
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except (typer.Exit, typer.Abort, ClickException):
            raise  # Do not capture click or typer exceptions
        except Exception:
            if RECURVE_TEST_MODE:
                raise  # Reraise exceptions during test mode
            traceback.print_exc()
            exit_with_error("An exception occurred.")

    return wrapper
