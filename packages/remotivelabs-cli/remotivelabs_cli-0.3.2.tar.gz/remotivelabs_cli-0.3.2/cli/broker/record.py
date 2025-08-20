from __future__ import annotations

from typing import List

import grpc
import typer

from cli.typer import typer_utils
from cli.utils.console import print_grpc_error, print_success

from .lib.broker import Broker

app = typer_utils.create_typer(help=help)


@app.command()
def start(
    filename: str = typer.Argument(..., help="Path to local file to upload"),
    namespace: List[str] = typer.Option(..., help="Namespace to record"),
    url: str = typer.Option(..., help="Broker URL", envvar="REMOTIVE_BROKER_URL"),
    api_key: str = typer.Option("offline", help="Cloud Broker API-KEY or access token", envvar="REMOTIVE_BROKER_API_KEY"),
) -> None:
    try:
        broker = Broker(url, api_key)
        broker.record_multiple(namespace, filename)
    except grpc.RpcError as rpc_error:
        print_grpc_error(rpc_error)


@app.command()
def stop(
    filename: str = typer.Argument(..., help="Path to local file to upload"),
    namespace: List[str] = typer.Option(..., help="Namespace to record"),
    url: str = typer.Option(..., help="Broker URL", envvar="REMOTIVE_BROKER_URL"),
    api_key: str = typer.Option("offline", help="Cloud Broker API-KEY or access token", envvar="REMOTIVE_BROKER_API_KEY"),
) -> None:
    try:
        broker = Broker(url, api_key)
        broker.stop_multiple(namespace, filename)
        print_success("Recording stopped")
    except grpc.RpcError as rpc_error:
        print_grpc_error(rpc_error)
