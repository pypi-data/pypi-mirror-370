import platform
import sys
from enum import Enum

import typer
from loguru import logger

from ._typer import RecurveTyper, exit_with_error
from .agent import agent_app
from .config import config_app
from .data import data_app
from .service import service_app

app = RecurveTyper(help="Reorc Agent Command Line Interface")
app.add_typer(agent_app, name="agent")
app.add_typer(config_app, name="config")
app.add_typer(service_app, name="service")
app.add_typer(data_app, name="data")


class LogLevel(str, Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


@app.callback()
def on_init(log_level: LogLevel = LogLevel.INFO):
    logger.remove()

    logger.add(sys.stderr, level=log_level)


@app.command()
async def version():
    """Show version information."""
    from recurvedata.agent._version import VERSION

    py_impl = platform.python_implementation()
    py_version = platform.python_version()
    system = platform.system()

    typer.echo(f"Running Reorc Agent {VERSION} with {py_impl} {py_version} on {system}.")


@app.command()
async def login():
    """Login the agent to the Reorc service."""
    from .._internal.agent import Agent
    from ..exceptions import UnauthorizedError

    agent = Agent.default()
    if agent.has_logged_in:
        yes: bool = typer.confirm("Agent already logged in. Do you want to re-login?", default=False)
        if not yes:
            return

    encoded_token: str = typer.prompt("Paste your API key", hide_input=True)

    try:
        await agent.login(encoded_token)
    except ValueError:
        exit_with_error("Invalid token.")
    except UnauthorizedError:
        exit_with_error("Invalid token.")
    except Exception as e:
        exit_with_error(f"Failed to login: {e}")

    typer.secho("Agent logged in.", fg="green")


@app.command()
async def logout():
    """Logout the agent from the Reorc service."""
    from .._internal.agent import Agent

    agent = Agent.default()
    if not agent.has_logged_in:
        exit_with_error("Agent not logged in.", fg=typer.colors.YELLOW)

    await agent.logout()


if __name__ == "__main__":
    app()
