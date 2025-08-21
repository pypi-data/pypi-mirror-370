# Typer Model Args
An extension for [Typer](https://typer.tiangolo.com/) that enables
model arguments.

Typer Model Args lets you declare Pydantic model parameters in your Typer command and automatically exposes its fields as proper Typer options/arguments on the command line. 
It keeps Typer’s annotations, adds missing ones when possible, and can convert typing.Literal fields into Enums for better CLI help and validation.

- Works with Typer
- Works with Pydantic models
- Preserves Typer metadata/annotations
- Optional Literal-to-Enum conversion for cleaner help and choices

## Installation

```shell
uv add typer_model_args
```

## Quickstart

```python
# app.py
import typer
from typing import Annotated
from pydantic import BaseModel
from typer_model_args import flatten_parameter_model_to_signature

class CliArgs(BaseModel):
    name: Annotated[str, typer.Option(...)]
    description: str | None = None

app = typer.Typer()

@app.command()
@flatten_parameter_model_to_signature()
def create(arguments: CliArgs, another_arg: str):
    """
    After decoration, --name/--description become top-level CLI options.
    """
    typer.echo(f"name={arguments.name}, desc={arguments.description}, extra={another_arg}")

if __name__ == "__main__":
    app()

```

## API

- `flatten_parameter_model_to_signature(*, literals_to_enums: bool = True)`
    - Flattens all pydantic model parameters in the decorated function into the function signature used by Typer.
    - `literals_to_enums`: when True, fields annotated with typing.Literal are turned into Enums so Typer can display and validate choices.


## Why use this?

- Keep your CLI schema and validation centralized in Pydantic models.
- Get clean, well-typed Typer commands without manually duplicating model fields as options.
- Better help messages and validation with minimal boilerplate.

## Requirements

- Python 3.10+
- Typer
- Pydantic

## License
MIT



