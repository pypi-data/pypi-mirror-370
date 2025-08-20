import inspect
from collections.abc import Callable
from typing import Any

from ._annotations import flatten_signature
from ._kwargs import rebuild_kwargs


def flatten_parameter_model_to_signature():
    """
    Flatten pydantic models to the signature of the decorated function.
    Keeps typer annotations while doing so and adds extra typer annotations
    if missing. Can handle Literals

    ## Example

    ```python
    from typerx import flatten_parameter_model_to_signature
    from pydantic import BaseModel

    class CliArgs(BaseModel):
        name: str
        description: str | None = None

    app = typer.Typer()

    @app.command()
    @flatten_parameter_model_to_signature()
    def trace_item(arguments: CliArgs, another_arg: str):
        return None
    ```
    """

    def decorator(function: Callable[[...], any]) -> Callable[[dict[str, Any]], any]:
        original_signature = inspect.signature(function)
        flat_signature = flatten_signature(original_signature)

        def wrapper(**kwargs):
            nonlocal flat_signature
            return function(**rebuild_kwargs(function.__name__, kwargs, flat_signature))

        wrapper.__signature__ = flat_signature.signature
        return wrapper # noqa

    return decorator
