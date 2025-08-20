from __future__ import annotations

import os
import sys
from typing import Any

import grpc
from rich.console import Console

console = Console(soft_wrap=True)
err_console = Console(stderr=True, soft_wrap=True)


def print_grpc_error(error: grpc.RpcError) -> None:
    if error.code() == grpc.StatusCode.UNAUTHENTICATED:
        is_access_token = os.environ["ACCESS_TOKEN"]
        if is_access_token is not None and is_access_token == "true":
            err_console.print(f":boom: [bold red]Authentication failed[/bold red]: {error.details()}")
            err_console.print("Please login again")
        else:
            err_console.print(":boom: [bold red]Authentication failed[/bold red]")
            err_console.print("Failed to verify api-key")
    else:
        err_console.print(f":boom: [bold red]Unexpected error, status code[/bold red]: {error.code()}")
        err_console.print(error.details())
    sys.exit(1)


def print_hint(message: str) -> None:
    err_console.print(f":point_right: [bold]{message}[/bold]")


def print_generic_error(message: str) -> None:
    err_console.print(f":boom: [bold red]Failed[/bold red]: {message}")


def print_success(message: str) -> None:
    console.print(f"[bold green]Success![/bold green] {message}")


def print_generic_message(message: str) -> None:
    console.print(f"[bold]{message}[/bold]")


def print_newline() -> None:
    """TODO: is this needed?"""
    console.print("\n")


def print_url(url: str) -> None:
    console.print(url, style="bold")


def print_unformatted(message: Any) -> None:
    """TODO: should we allow this?"""
    console.print(message)


def print_unformatted_to_stderr(message: Any) -> None:
    """TODO: should we allow this?"""
    err_console.print(message)
