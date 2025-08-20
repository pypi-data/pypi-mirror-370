import typer

from ._typer import RecurveTyper, exit_with_error

PROJECT_NAME = "recurve_services"

data_app: typer.Typer = RecurveTyper(name="data", help="Commands for managing data, e.g. volumes.")


@data_app.command()
async def clear():
    """Clear data."""
    import docker

    client = docker.from_env()
    try:
        client.ping()
    except Exception as e:
        exit_with_error(f"Failed to connect to Docker: {e}")

    filters = {"name": f"{PROJECT_NAME}_*"}
    volumes = client.volumes.list(filters=filters)
    typer.echo("Starting to clear data")
    for volume in volumes:
        try:
            volume.remove(force=True)
            typer.echo(f"Removed volume {volume.name}")
        except Exception as e:
            exit_with_error(f"Failed to remove volume {volume.name}: {e}")

    typer.echo("Successfully cleared data.")
