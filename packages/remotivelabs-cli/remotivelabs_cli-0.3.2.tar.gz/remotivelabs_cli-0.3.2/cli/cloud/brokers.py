from __future__ import annotations

import json
import os
import signal as os_signal
from typing import Any, Union

import requests
import typer
import websocket

from cli.typer import typer_utils
from cli.utils.console import print_generic_message
from cli.utils.rest_helper import RestHelper as Rest

app = typer_utils.create_typer()


@app.command("list", help="Lists brokers in project")
def list(project: str = typer.Option(..., help="Project ID", envvar="REMOTIVE_CLOUD_PROJECT")) -> None:
    Rest.handle_get(f"/api/project/{project}/brokers")


@app.command("describe", help="Shows details about a specific broker")
def describe(name: str, project: str = typer.Option(..., help="Project ID", envvar="REMOTIVE_CLOUD_PROJECT")) -> None:
    Rest.handle_get(f"/api/project/{project}/brokers/{name}")


@app.command("delete", help="Stops and deletes a broker from project")
def stop(name: str, project: str = typer.Option(..., help="Project ID", envvar="REMOTIVE_CLOUD_PROJECT")) -> None:
    Rest.handle_delete(f"/api/project/{project}/brokers/{name}")


@app.command(help="Deletes your personal broker from project")
def delete_personal(project: str = typer.Option(..., help="Project ID", envvar="REMOTIVE_CLOUD_PROJECT")) -> None:
    Rest.handle_delete(f"/api/project/{project}/brokers/personal")


def do_start(name: str, project: str, api_key: str, tag: str, return_response: bool = False) -> Union[requests.Response, None]:
    if tag == "":
        tag_to_use = None
    else:
        tag_to_use = tag

    if api_key == "":
        body = {"size": "S", "tag": tag_to_use}
    else:
        body = {"size": "S", "apiKey": api_key, "tag": tag_to_use}
    return Rest.handle_post(
        f"/api/project/{project}/brokers/{name}",
        body=json.dumps(body),
        return_response=return_response,
        progress_label=f"Starting {name}...",
    )


@app.command(name="create", help="Create a broker in project")
def start(
    name: str,
    project: str = typer.Option(..., help="Project ID", envvar="REMOTIVE_CLOUD_PROJECT"),
    tag: str = typer.Option("", help="Optional specific tag/version"),
    silent: bool = typer.Option(False, help="Optional specific tag/version"),
    api_key: str = typer.Option("", help="Start with your own api-key"),
) -> None:
    do_start(name, project, api_key, tag, return_response=silent)


@app.command(name="logs")
def logs(
    broker_name: str = typer.Argument(..., help="Broker name to see logs for"),
    tail: bool = typer.Option(False, help="Tail the broker log"),
    history_minutes: str = typer.Option(10, help="History in minutes minutes to fetch"),
    project: str = typer.Option(..., help="Project ID", envvar="REMOTIVE_CLOUD_PROJECT"),
) -> None:
    """
    Exposes broker logs history or real-time tail of the broker.

    When using --tail option, --history always skipped even if supplied
    """

    def exit_on_ctrlc(_sig: Any, _frame: Any) -> None:
        wsapp.close()
        os._exit(0)

    os_signal.signal(os_signal.SIGINT, exit_on_ctrlc)

    def on_message(_wsapp: Any, message: str) -> None:
        # TODO: use log instead of print for debug information?
        print_generic_message(message)

    def on_error(_wsapp: Any, err: str) -> None:
        # TODO: use log instead of print for debug information?
        print_generic_message(f"Error encountered: {err}")

    Rest.ensure_auth_token()
    # This will work with both http -> ws and https -> wss
    ws_url = Rest.get_base_url().replace("http", "ws")

    if tail:
        q = "?tail=yes"
    elif history_minutes != "10":
        q = f"?history={history_minutes}"
    else:
        q = ""

    wsapp = websocket.WebSocketApp(
        f"{ws_url}/api/project/{project}/brokers/{broker_name}/logs{q}", header=Rest.get_headers(), on_message=on_message, on_error=on_error
    )
    wsapp.run_forever()
