from typing import Any

import typer
from click import Context
from typer.core import TyperGroup

from cli.utils.console import print_generic_message


class OrderCommands(TyperGroup):
    def list_commands(self, _ctx: Context):  # type: ignore
        return list(self.commands)


def create_typer(**kwargs: Any) -> typer.Typer:
    """Create a Typer instance with default settings."""
    return typer.Typer(cls=OrderCommands, no_args_is_help=True, invoke_without_command=True, **kwargs)


def print_padded(label: str, right_text: str, length: int = 30) -> None:
    padded_label = label.ljust(length)  # pad to 30 characters
    print_generic_message(f"{padded_label} {right_text}")
