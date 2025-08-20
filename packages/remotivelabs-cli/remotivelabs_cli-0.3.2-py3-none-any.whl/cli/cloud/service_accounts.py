from __future__ import annotations

import json
from typing import List

import typer

from cli.typer import typer_utils
from cli.utils.rest_helper import RestHelper as Rest

from . import service_account_tokens

app = typer_utils.create_typer()


@app.command(name="list", help="List service-accounts")
def list_service_accounts(project: str = typer.Option(..., help="Project ID", envvar="REMOTIVE_CLOUD_PROJECT")) -> None:
    Rest.handle_get(f"/api/project/{project}/admin/accounts")


ROLES_DESCRIPTION = """
    [bold]Supported roles [/bold]
    project/admin          - Full project support, view, edit, delete and manage users
    project/user           - View, edit, upload, delete but no admin
    project/viewer         - View only
    project/storageCreator - Can upload to storage but not view, overwrite or delete
    org/topologyRunner     - Can start RemotiveTopology
"""


@app.command(
    name="create",
    help=f"""
    Create a new service account with one or more roles.

    [bold]Must only use lowercase letters, digits, or dashes, and must not contain -- or end with a dash.[/bold]

    remotive cloud service-accounts create --role project/user --role project/storageCreator
    {ROLES_DESCRIPTION}
    """,
)
def create_service_account(
    name: str,
    role: List[str] = typer.Option(..., help="Roles to apply"),
    project: str = typer.Option(..., help="Project ID", envvar="REMOTIVE_CLOUD_PROJECT"),
) -> None:
    data = {"name": name, "roles": role}
    Rest.handle_post(url=f"/api/project/{project}/admin/accounts", body=json.dumps(data))


@app.command(
    name="update",
    help=f"""
    Update an existing service account with one or more roles.

    remotive cloud service-accounts update --role project/user --role project/storageCreator
    {ROLES_DESCRIPTION}
    """,
)
def update_service_account(
    service_account: str = typer.Argument(..., help="Service account name"),
    role: List[str] = typer.Option(..., help="Roles to apply"),
    project: str = typer.Option(..., help="Project ID", envvar="REMOTIVE_CLOUD_PROJECT"),
) -> None:
    Rest.handle_put(url=f"/api/project/{project}/admin/accounts/{service_account}", body=json.dumps({"roles": role}))


@app.command(name="delete", help="Delete service account")
def delete_service_account(name: str, project: str = typer.Option(..., help="Project ID", envvar="REMOTIVE_CLOUD_PROJECT")) -> None:
    Rest.handle_delete(url=f"/api/project/{project}/admin/accounts/{name}")


app.add_typer(service_account_tokens.app, name="tokens", help="Manage project service account access tokens")
