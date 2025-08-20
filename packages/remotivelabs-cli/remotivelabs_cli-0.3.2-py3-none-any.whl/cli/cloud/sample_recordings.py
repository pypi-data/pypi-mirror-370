import json

import typer

from cli.typer import typer_utils
from cli.utils.rest_helper import RestHelper as Rest

app = typer_utils.create_typer()


@app.command(name="import", help="Import sample recording into project")
def do_import(
    recording_session: str = typer.Argument(..., help="Recording session id"),
    project: str = typer.Option(..., help="Project to import sample recording into", envvar="REMOTIVE_CLOUD_PROJECT"),
) -> None:
    Rest.handle_post(url=f"/api/samples/files/recording/{recording_session}/copy", body=json.dumps({"projectUid": project}))


@app.command("list")
def list() -> None:
    """
    List available sample recordings
    """

    Rest.handle_get("/api/samples/files/recording")
