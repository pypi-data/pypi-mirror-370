import json

import typer

from cli.typer import typer_utils
from cli.utils.console import print_generic_error, print_generic_message
from cli.utils.rest_helper import RestHelper as Rest

app = typer_utils.create_typer()


@app.command(name="list", help="List your projects")
def list_projects(organization: str = typer.Option(..., help="Organization ID", envvar="REMOTIVE_CLOUD_ORGANIZATION")) -> None:
    r = Rest.handle_get(url=f"/api/bu/{organization}/me", return_response=True)
    if r is None:
        return

    if r.status_code == 200:
        # extract the project uid parts
        projects = r.json()["projects"]
        projects = map(lambda p: p["uid"], projects)
        print_generic_message(json.dumps(list(projects)))
    else:
        print_generic_error(f"Got unexpected status {r.status_code}\n")


@app.command(name="create")
def create_project(
    project_uid: str = typer.Argument(help="Project UID"),
    organization: str = typer.Option(..., help="Organization ID", envvar="REMOTIVE_CLOUD_ORGANIZATION"),
    project_display_name: str = typer.Option(default="", help="Project display name"),
) -> None:
    create_project_req = {
        "uid": project_uid,
        "displayName": project_display_name if project_display_name != "" else project_uid,
        "description": "",
    }

    Rest.handle_post(url=f"/api/bu/{organization}/project", body=json.dumps(create_project_req))


@app.command(name="delete")
def delete(project: str = typer.Argument(help="Project ID", envvar="REMOTIVE_CLOUD_PROJECT")) -> None:
    Rest.handle_delete(url=f"/api/project/{project}")
