import json
from typing import Any, Optional

import typer

from ..config import CONFIG, parse_value
from ._typer import RecurveTyper, exit_with_error

config_app = RecurveTyper(help="Commands for interacting with the configurations.")


@config_app.command()
def view(
    show_secrets: Optional[bool] = typer.Option(
        False, "--show-secrets/--hide-secrets", help="Display the secret setting values."
    ),
):
    """Display the current configurations."""
    data: dict[str, Any] = CONFIG.model_dump()
    if show_secrets:
        data["token"] = CONFIG.token.get_secret_value()
    if not CONFIG.is_valid():
        typer.secho("Warning: Configuration is incomplete.", fg="yellow")
    typer.secho(json.dumps(data, indent=2, default=str))


@config_app.command()
def get(key: str):
    """Get the value of a configuration key."""
    data: dict[str, Any] = CONFIG.model_dump()
    if key not in data:
        typer.secho(f"Key '{key}' not found.", fg="red")
    else:
        typer.echo(f"{key}: {data[key]}")


@config_app.command()
def set(key: str, value: str):
    """Set the value of a configuration key."""
    allowed_keys = CONFIG.editable_fields
    if key not in allowed_keys:
        exit_with_error(f"Invalid configuration key: {key}, allowed keys: {allowed_keys}")

    try:
        parsed_value = parse_value(key, value)
        setattr(CONFIG, key, parsed_value)
        CONFIG.save()
        typer.secho(f"Set {key} to {value}.", fg="green")
    except Exception as e:
        exit_with_error(f"Error setting {key}: {e}")
