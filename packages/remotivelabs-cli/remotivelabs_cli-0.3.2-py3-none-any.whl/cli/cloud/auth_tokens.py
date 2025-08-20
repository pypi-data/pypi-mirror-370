from __future__ import annotations

from typing import List, Optional

import typer
from rich.table import Table

from cli.cloud.organisations import do_select_default_org
from cli.settings import settings
from cli.settings.token_file import TokenFile
from cli.utils.console import print_generic_error, print_generic_message, print_hint, print_newline, print_success, print_unformatted
from cli.utils.rest_helper import RestHelper as Rest


def _prompt_choice(  # noqa: C901
    choices: List[TokenFile],
    skip_prompt: bool = False,
    info_message: Optional[str] = None,
) -> Optional[TokenFile]:
    accounts = settings.list_accounts()

    table = Table("#", "Active", "Type", "Token", "Account", "Created", "Expires")

    included_tokens: list[TokenFile] = []
    excluded_tokens: list[TokenFile] = []

    for token in choices:
        account = accounts.get(token.account.email)
        if account and account.credentials_file:
            token_file = settings.get_token_file(account.credentials_file)
            if token_file and token_file.name in (token.name or ""):
                included_tokens.append(token)
            else:
                excluded_tokens.append(token)
        else:
            excluded_tokens.append(token)

    if len(included_tokens) == 0:
        return None

    included_tokens.sort(key=lambda token: token.created, reverse=True)

    active_token = settings.get_active_token_file()
    active_token_index = None
    for idx, choice in enumerate(included_tokens, start=1):
        is_active = active_token is not None and active_token.name == choice.name
        active_token_index = idx if is_active else active_token_index

        table.add_row(
            f"[yellow]{idx}",
            ":white_check_mark:" if is_active else "",
            "user" if choice.type == "authorized_user" else "sa",
            choice.name,
            f"[bold]{choice.account.email if choice.account else 'unknown'}[/bold]",
            str(choice.created),
            str(choice.expires),
        )
    print_unformatted(table)

    if skip_prompt:
        return None

    print_newline()
    if info_message:
        print_generic_message(info_message)

    selection = typer.prompt(
        f"Enter the number(# 1-{len(included_tokens)}) of the account to select (q to quit)",
        default=f"{active_token_index}" if active_token_index is not None else None,
    )

    if selection == "q":
        return None
    try:
        index = int(selection) - 1
        if 0 <= index < len(included_tokens):
            return included_tokens[index]
        raise ValueError
    except ValueError:
        typer.echo("Invalid choice, please try again")
        return _prompt_choice(included_tokens, skip_prompt, info_message)


def prompt_to_set_org() -> None:
    active_account = settings.get_active_account()
    if active_account and not active_account.default_organization:
        set_default_organisation = typer.confirm(
            "You have not set a default organization\nWould you like to choose one now?",
            abort=False,
            default=True,
        )
        if set_default_organisation:
            do_select_default_org(get=False)


def do_activate(token_name: Optional[str]) -> Optional[TokenFile]:
    if token_name:
        token_file = settings.get_token_file(token_name)
        if not token_file:
            print_generic_error(f"Token with filename or name {token_name} could not be found")
            return None
        return settings.activate_token(token_file)

    token_files = settings.list_personal_token_files()
    token_files.extend(settings.list_service_account_token_files())
    if len(token_files) > 0:
        token_selected = list_and_select_personal_token(include_service_accounts=True)
        if token_selected is not None:
            is_logged_in = Rest.has_access("/api/whoami")
            if not is_logged_in:
                print_generic_error("Could not access RemotiveCloud with selected token")
            else:
                print_success("Access to RemotiveCloud granted")
                # Only select default if activate was done with selection and successful
                # and not SA since SA cannot list available organizations
                if token_selected.type == "authorized_user":
                    prompt_to_set_org()
        return token_selected

    print_hint("No credentials available, login to activate credentials")
    return None


def list_and_select_personal_token(
    skip_prompt: bool = False,
    include_service_accounts: bool = False,
    info_message: Optional[str] = None,
) -> Optional[TokenFile]:
    personal_tokens = settings.list_personal_token_files()

    if include_service_accounts:
        sa_tokens = settings.list_service_account_token_files()
        personal_tokens.extend(sa_tokens)

    selected_token = _prompt_choice(personal_tokens, skip_prompt=skip_prompt, info_message=info_message)
    if selected_token is not None:
        settings.activate_token(selected_token)

    return selected_token
