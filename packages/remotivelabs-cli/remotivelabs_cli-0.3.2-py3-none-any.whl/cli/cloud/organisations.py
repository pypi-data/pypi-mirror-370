from __future__ import annotations

import json
from dataclasses import dataclass
from typing import List, Optional

import typer
from rich.table import Table

from cli.settings import settings
from cli.typer import typer_utils
from cli.utils.console import print_generic_error, print_generic_message, print_hint, print_newline, print_unformatted_to_stderr
from cli.utils.rest_helper import RestHelper

app = typer_utils.create_typer()


@dataclass
class Organisation:
    display_name: str
    uid: str


def _prompt_choice(choices: List[Organisation]) -> Optional[Organisation]:
    table = Table("#", "Name", "Uid", "Default")

    account = settings.get_active_account()
    current_default_org = account.default_organization if account else None

    for idx, choice in enumerate(choices, start=1):
        table.add_row(
            f"[yellow]{idx}",
            f"[bold]{choice.display_name}[/bold]",
            choice.uid,
            ":thumbsup:" if current_default_org is not None and current_default_org == choice.uid else "",
        )
    print_unformatted_to_stderr(table)

    print_newline()
    selection = typer.prompt(f"Enter the number(# 1-{len(choices)}) of the organization to select (or q to quit)")

    if selection == "q":
        return None
    try:
        index = int(selection) - 1
        if 0 <= index < len(choices):
            return choices[index]
        raise ValueError
    except ValueError:
        print_generic_error("Invalid choice, please try again")
        return _prompt_choice(choices)


@app.command("default")
def select_default_org(
    organization_uid: str = typer.Argument(None, help="Organization uid or empty to select one"),
    get: bool = typer.Option(False, help="Print current default organization"),
) -> None:
    do_select_default_org(organization_uid, get)


def do_select_default_org(organisation_uid: Optional[str] = None, get: bool = False) -> None:
    r"""
    Set default organization for the currently activated user, empty to choose from available organizations or organization uid as argument

    remotive cloud organizations default my_org \[set specific org uid]
    remotive cloud organizations default \[select one from prompt]
    remotive cloud organizations default --get \[print current default]

    Note that service-accounts does Not have permission to list organizations and will get a 403 Forbidden response so you must
    select the organization uid as argument
    """
    active_account = settings.get_active_account()
    if get:
        if active_account and active_account.default_organization:
            print_unformatted_to_stderr(active_account.default_organization)
        else:
            print_unformatted_to_stderr("No default organization set")
    elif organisation_uid is not None:
        settings.set_default_organisation(organisation_uid)
    else:
        if active_account:
            token = settings.get_token_file(active_account.credentials_file)
            if token and token.type != "authorized_user":
                print_hint(
                    "You must supply the organization name as argument when using a service-account since the "
                    "service-account is not allowed to list"
                )
                return

        r = RestHelper.handle_get("/api/bu", return_response=True)
        orgs = r.json()
        orgs = [Organisation(display_name=o["organisation"]["displayName"], uid=o["organisation"]["uid"]) for o in orgs]

        selected = _prompt_choice(orgs)

        if selected is not None:
            typer.echo(f"Default organisation: {selected.display_name} (uid: {selected.uid})")
            settings.set_default_organisation(selected.uid)


@app.command(name="list", help="List your available organizations")
def list_orgs() -> None:
    r = RestHelper.handle_get("/api/bu", return_response=True)
    orgs = [{"uid": org["organisation"]["uid"], "displayName": org["organisation"]["displayName"]} for org in r.json()]
    print_generic_message(json.dumps(orgs))
