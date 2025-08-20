import json

import typer

from cli.settings import settings
from cli.typer import typer_utils
from cli.utils.console import print_generic_message, print_success
from cli.utils.rest_helper import RestHelper as Rest

app = typer_utils.create_typer()


# TODO: add add interactive flag to set target directory
@app.command(name="create", help="Create and download a new service account access token")
def create(
    expire_in_days: int = typer.Option(default=365, help="Number of this token is valid"),
    service_account: str = typer.Option(..., help="Service account name"),
    project: str = typer.Option(..., help="Project ID", envvar="REMOTIVE_CLOUD_PROJECT"),
) -> None:
    response = Rest.handle_post(
        url=f"/api/project/{project}/admin/accounts/{service_account}/keys",
        return_response=True,
        body=json.dumps({"daysUntilExpiry": expire_in_days}),
    )

    sat = settings.add_service_account_token(response.text)
    print_success(f"Service account access token added: {sat.name}")
    print_generic_message("This file contains secrets and must be kept safe")


@app.command(name="list", help="List service account access tokens")
def list_tokens(
    service_account: str = typer.Option(..., help="Service account name"),
    project: str = typer.Option(..., help="Project ID", envvar="REMOTIVE_CLOUD_PROJECT"),
) -> None:
    Rest.handle_get(f"/api/project/{project}/admin/accounts/{service_account}/keys")


@app.command(name="describe", help="Describe service account access token")
def describe(
    name: str = typer.Argument(..., help="Access token name"),
    service_account: str = typer.Option(..., help="Service account name"),
    project: str = typer.Option(..., help="Project ID", envvar="REMOTIVE_CLOUD_PROJECT"),
) -> None:
    Rest.handle_get(f"/api/project/{project}/admin/accounts/{service_account}/keys/{name}")


@app.command(name="revoke", help="Revoke service account access token")
def revoke(
    name: str = typer.Argument(..., help="Access token name"),
    delete: bool = typer.Option(True, help="Also deletes the token after revocation"),
    service_account: str = typer.Option(..., help="Service account name"),
    project: str = typer.Option(..., help="Project ID", envvar="REMOTIVE_CLOUD_PROJECT"),
) -> None:
    res = Rest.handle_get(f"/api/project/{project}/admin/accounts/{service_account}/keys/{name}", return_response=True)
    if not res.json()["revoked"]:
        Rest.handle_patch(f"/api/project/{project}/admin/accounts/{service_account}/keys/{name}/revoke", quiet=True)
    if delete:
        Rest.handle_delete(f"/api/project/{project}/admin/accounts/{service_account}/keys/{name}", quiet=True)
        token_with_name = [token for token in settings.list_service_account_token_files() if token.name == name]
        if len(token_with_name) > 0:
            settings.remove_token_file(name)
