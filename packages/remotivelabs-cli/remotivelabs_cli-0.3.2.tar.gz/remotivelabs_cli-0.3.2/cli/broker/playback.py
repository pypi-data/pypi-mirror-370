from __future__ import annotations

from typing import Dict, List

import grpc
import typer

from cli.typer import typer_utils
from cli.utils.console import print_generic_error, print_generic_message, print_grpc_error, print_success

from .lib.broker import Broker

app = typer_utils.create_typer(help=help)


def recording_and_namespace(recording: str) -> Dict[str, str]:
    splitted = recording.split("::")
    if len(splitted) != 2:
        print_generic_error("Invalid --recording option, expected file_name::namespace")
        raise typer.Exit(1)
    return {"recording": splitted[0], "namespace": splitted[1]}


@app.command()
def play(
    recording: List[str] = typer.Option(..., help="Which recording and which namespace to play"),
    url: str = typer.Option(..., help="Broker URL", envvar="REMOTIVE_BROKER_URL"),
    api_key: str = typer.Option("offline", help="Cloud Broker API-KEY or access token", envvar="REMOTIVE_BROKER_API_KEY"),
) -> None:
    """
    Play recording files on broker.

    Separate recording file and namespace with ::

    remotive broker playback play --recording myrecording_can0::can0 --recording myrecording_can1::can1
    """

    rec = list(map(recording_and_namespace, recording))
    try:
        broker = Broker(url, api_key)
        status = broker.play(rec)
        # TODO: use log instead of print for debug information?
        print_generic_message(str(status))
    except grpc.RpcError as err:
        print_grpc_error(err)


@app.command()
def stop(
    recording: List[str] = typer.Option(..., help="Which recording and which namespace to stop"),
    url: str = typer.Option(..., help="Broker URL", envvar="REMOTIVE_BROKER_URL"),
    api_key: str = typer.Option("offline", help="Cloud Broker API-KEY or access token", envvar="REMOTIVE_BROKER_API_KEY"),
) -> None:
    """
    Stop recordings that are beeing played on brokers are done with the same syntax as when you start them.

    Separate recording file and namespace with ::

    remotive broker playback stop --recording myrecording_can0::can0 --recording myrecording_can1::can1
    """

    rec = list(map(recording_and_namespace, recording))

    try:
        broker = Broker(url, api_key)
        broker.stop_play(rec)
        print_success("Recording stopped")
    except grpc.RpcError as err:
        print_grpc_error(err)


@app.command()
def pause(
    recording: List[str] = typer.Option(..., help="Which recording and which namespace to stop"),
    url: str = typer.Option(..., help="Broker URL", envvar="REMOTIVE_BROKER_URL"),
    api_key: str = typer.Option("offline", help="Cloud Broker API-KEY or access token", envvar="REMOTIVE_BROKER_API_KEY"),
) -> None:
    """
    Pause recordings that are beeing played on brokers are done with the same syntax as when you start them.

    Separate recording file and namespace with ::

    remotive broker playback pause --recording myrecording_can0::can0 --recording myrecording_can1::can1
    """

    rec = list(map(recording_and_namespace, recording))
    try:
        broker = Broker(url, api_key)
        broker.pause_play(rec)
        print_success("Recording paused")
    except grpc.RpcError as err:
        print_grpc_error(err)


@app.command()
def seek(
    recording: List[str] = typer.Option(..., help="Which recording and which namespace to stop"),
    seconds: float = typer.Option(..., help="Target offset in seconds"),
    url: str = typer.Option(..., help="Broker URL", envvar="REMOTIVE_BROKER_URL"),
    api_key: str = typer.Option("offline", help="Cloud Broker API-KEY or access token", envvar="REMOTIVE_BROKER_API_KEY"),
) -> None:
    """
    Seeks to a position in seconds into the recording

    Separate recording file and namespace with ::

    remotive broker playback seek --recording myrecording_can0::can0 --recording myrecording_can1::can1 --seconds 23
    """

    broker = Broker(url, api_key)

    rec = list(map(recording_and_namespace, recording))

    try:
        broker = Broker(url, api_key)
        broker.seek(rec, int(seconds * 1000000))
    except grpc.RpcError as err:
        print_grpc_error(err)
