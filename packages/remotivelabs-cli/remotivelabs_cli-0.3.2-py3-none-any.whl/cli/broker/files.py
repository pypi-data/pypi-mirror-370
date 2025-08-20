from __future__ import annotations

import os
from typing import List

import grpc
import typer
from rich.progress import Progress, SpinnerColumn, TextColumn

from cli.typer import typer_utils
from cli.utils.console import print_generic_error, print_grpc_error, print_success

from .lib.broker import Broker

app = typer_utils.create_typer(help=help)


@app.command()
def reload_configuration(
    url: str = typer.Option(..., help="Broker URL", envvar="REMOTIVE_BROKER_URL"),
    api_key: str = typer.Option("offline", help="Cloud Broker API-KEY or access token", envvar="REMOTIVE_BROKER_API_KEY"),
) -> None:
    try:
        broker = Broker(url, api_key)
        broker.reload_config()
        print_success("Configuration reloaded")
    except grpc.RpcError as err:
        print_grpc_error(err)


@app.command()
def delete(
    path: List[str] = typer.Argument(..., help="Paths to files on broker to delete"),
    exit_on_failure: bool = typer.Option(False, help="Exits if there was a problem deleting a file"),
    url: str = typer.Option(..., help="Broker URL", envvar="REMOTIVE_BROKER_URL"),
    api_key: str = typer.Option("offline", help="Cloud Broker API-KEY or access token", envvar="REMOTIVE_BROKER_API_KEY"),
) -> None:
    """
    Deletes the specified files from the broker
    """
    try:
        broker = Broker(url, api_key)

        if len(path) == 0:
            print_generic_error("At least one path must be suppled")
            raise typer.Exit(1)

        broker.delete_files(path, exit_on_failure)
    except grpc.RpcError as err:
        print_grpc_error(err)


@app.command()
def download(
    path: str = typer.Argument(..., help="Path to file on broker to download"),
    output: str = typer.Option("", help="Optional output file name"),
    url: str = typer.Option(..., help="Broker URL", envvar="REMOTIVE_BROKER_URL"),
    api_key: str = typer.Option("offline", help="Cloud Broker API-KEY or access token", envvar="REMOTIVE_BROKER_API_KEY"),
) -> None:
    """
    Downloads a file from a broker
    """
    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True,
        ) as progress:
            progress.add_task(description=f"Downloading {path}...", total=None)
            broker = Broker(url, api_key)
            output_file = os.path.basename(path)
            if output != "":
                output_file = output
            if os.path.exists(output_file):
                print_generic_error(f"File already exist {output_file}, please use another output file name")
            else:
                broker.download(path, output_file)
                print_success(f"{output_file} saved")
    except grpc.RpcError as err:
        print_grpc_error(err)


@app.command()
def upload(
    path: str = typer.Argument(..., help="Path to local file to upload"),
    output: str = typer.Option("", help="Optional output path on broker"),
    url: str = typer.Option(..., help="Broker URL", envvar="REMOTIVE_BROKER_URL"),
    api_key: str = typer.Option("offline", help="Cloud Broker API-KEY or access token", envvar="REMOTIVE_BROKER_API_KEY"),
) -> None:
    """
    Uploads a file to a broker - physical or in cloud.
    """
    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True,
        ) as progress:
            progress.add_task(description=f"Uploading {path}...", total=None)

            if path == ".":
                path = "./"  ## Does not work otherwise

            if not os.path.exists(path):
                print_generic_error(f"File {path} does not exist")
                raise typer.Exit(1)

            broker = Broker(url, api_key)

            if os.path.isdir(path):
                broker.upload_folder(path)
                print_success(f"{path} uploaded")
            else:
                output_file = os.path.basename(path)
                if output != "":
                    output_file = output
                broker.upload(path, output_file)
                print_success(f"{path} uploaded")
    except grpc.RpcError as err:
        print_grpc_error(err)
