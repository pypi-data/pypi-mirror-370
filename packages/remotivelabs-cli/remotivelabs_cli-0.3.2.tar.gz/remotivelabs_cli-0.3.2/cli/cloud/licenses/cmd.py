import typer

from cli.typer import typer_utils
from cli.utils.rest_helper import RestHelper

app = typer_utils.create_typer()


@app.command(help="List licenses for an organization")
def licenses(
    organization: str = typer.Option(..., help="Organization ID", envvar="REMOTIVE_CLOUD_ORGANIZATION"),
    filter_option: str = typer.Option("all", help="all, valid, expired"),
) -> None:
    RestHelper.handle_get(f"/api/bu/{organization}/licenses", {"filter": filter_option})
