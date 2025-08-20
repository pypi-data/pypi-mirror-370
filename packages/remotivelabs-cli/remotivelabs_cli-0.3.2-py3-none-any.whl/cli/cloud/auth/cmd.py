from __future__ import annotations

import os
import sys

import typer
from rich.console import Console
from rich.table import Table

from cli.cloud.auth.login import login as do_login
from cli.settings import settings
from cli.typer import typer_utils
from cli.utils.console import print_generic_error, print_generic_message, print_success, print_unformatted
from cli.utils.rest_helper import RestHelper as Rest

from .. import auth_tokens

console = Console(stderr=False)

HELP = """
Manage how you authenticate with our cloud platform
"""
app = typer_utils.create_typer(help=HELP)


@app.command(name="login")
def login(browser: bool = typer.Option(default=True, help="Does not automatically open browser, instead shows a link")) -> None:
    """
    Login to the cli using browser

    If not able to open a browser it will show fallback to headless login and show a link that
    users can copy into any browser when this is unsupported where running the cli - such as in docker,
    virtual machine or ssh sessions.
    """
    do_login(headless=not browser)


@app.command()
def whoami() -> None:
    """
    Validates authentication and fetches your account information
    """
    Rest.handle_get("/api/whoami")


@app.command()
def print_access_token(
    account: str = typer.Option(None, help="Email of the account you want to print access token for, defaults to active"),
) -> None:
    """
    Print current active access token or the token for the specified account
    """
    if not account:
        active_token = settings.get_active_token() or os.getenv("REMOTIVE_CLOUD_ACCESS_TOKEN", None)
        if not active_token:
            print_generic_error("You have no active account")
            sys.exit(1)

        print_generic_message(active_token)
        return

    accounts = settings.list_accounts()
    if account not in accounts:
        print_generic_error(f"No account for {account} was found")
        sys.exit(1)

    token_file_name = accounts[account].credentials_file
    token_file = settings.get_token_file(token_file_name)
    if not token_file:
        print_generic_error(f"Token file for {account} could not be found")
        sys.exit(1)

    print_generic_message(token_file.token)


def print_access_token_file() -> None:
    """
    Print current active token and its metadata
    """
    active_token_file = settings.get_active_token_file()
    if not active_token_file:
        print_generic_error("You have no active account")
        sys.exit(1)

    print_generic_message(str(active_token_file))


@app.command(name="deactivate")
def deactivate() -> None:
    """
    Clears active account
    """
    settings.clear_active_account()
    print_success("Account no longer active")


@app.command("activate")
def activate(token_name: str = typer.Argument(None, help="Name, filename or path to a credentials file")) -> None:
    """
    Set the active account
    """
    auth_tokens.do_activate(token_name)


@app.command(name="list")
def list() -> None:
    """
    Lists available credential files on filesystem

    TODO: Support output format
    """
    accounts = settings.list_accounts()

    table = Table("#", "Active", "Type", "Token", "Account", "Organization", "Created", "Expires")
    for idx, (email, account) in enumerate(accounts.items(), start=1):
        token_file = settings.get_token_file_by_email(email)
        is_active = settings.is_active_account(email)

        table.add_row(
            f"[yellow]{idx}",
            ":white_check_mark:" if is_active else "",
            "unknown" if not token_file else "user" if token_file.type == "authorized_user" else "sa",
            token_file.name if token_file else "",
            f"[bold]{email}[/bold]",
            account.default_organization if account.default_organization else "",
            str(token_file.created) if token_file else "",
            str(token_file.expires) if token_file else "",
        )
    print_unformatted(table)
