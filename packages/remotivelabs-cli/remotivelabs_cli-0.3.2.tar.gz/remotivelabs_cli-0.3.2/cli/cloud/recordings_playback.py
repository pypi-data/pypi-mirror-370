from __future__ import annotations

import datetime
import json
import os
import sys
import tempfile
from pathlib import Path
from typing import Any, List, Union

import grpc
import typer
from rich.progress import Progress, SpinnerColumn, TextColumn

from cli.utils.console import print_generic_error, print_generic_message, print_grpc_error, print_hint, print_unformatted
from cli.utils.rest_helper import RestHelper as Rest

from ..broker.lib.broker import Broker, SubscribableSignal
from ..typer import typer_utils

app = typer_utils.create_typer(
    help="""
Support for playback of a recording on a cloud broker, make sure to always mount a recording first
"""
)


@app.command()
def play(
    recording_session: str = typer.Argument(..., help="Recording session id", envvar="REMOTIVE_CLOUD_RECORDING_SESSION"),
    broker: str = typer.Option(None, help="Broker to use"),
    project: str = typer.Option(..., help="Project ID", envvar="REMOTIVE_CLOUD_PROJECT"),
    show_progress: bool = typer.Option(False, help="Show progress after started playing"),
    repeat: bool = typer.Option(False, help="Repeat recording - must keep command running in terminal"),
) -> None:
    """
    Start playing a recording.
    There is no problem invoking play multiple times since if it is already playing the command will be ignored.
    Use --repeat to have the recording replayed when it reaches the end.
    """

    _do_change_playback_mode("play", recording_session, broker, project, progress_on_play=show_progress, repeat=repeat)


@app.command()
def pause(
    recording_session: str = typer.Argument(..., help="Recording session id", envvar="REMOTIVE_CLOUD_RECORDING_SESSION"),
    broker: str = typer.Option(None, help="Broker to use"),
    project: str = typer.Option(..., help="Project ID", envvar="REMOTIVE_CLOUD_PROJECT"),
) -> None:
    """
    Pause a recording
    """
    _do_change_playback_mode("pause", recording_session, broker, project)


@app.command()
def progress(
    recording_session: str = typer.Argument(..., help="Recording session id", envvar="REMOTIVE_CLOUD_RECORDING_SESSION"),
    broker: str = typer.Option(None, help="Broker to use"),
    project: str = typer.Option(..., help="Project ID", envvar="REMOTIVE_CLOUD_PROJECT"),
) -> None:
    """
    Shows progress of the recording playing.
    Use --repeat to have the recording replayed when it reaches the end.
    """
    _do_change_playback_mode("status", recording_session, broker, project)


@app.command()
def seek(
    recording_session: str = typer.Argument(..., help="Recording session id", envvar="REMOTIVE_CLOUD_RECORDING_SESSION"),
    seconds: int = typer.Option(..., min=0, help="Target offset in seconds"),
    broker: str = typer.Option(None, help="Broker to use"),
    project: str = typer.Option(..., help="Project ID", envvar="REMOTIVE_CLOUD_PROJECT"),
) -> None:
    """
    Seek seconds into a recording
    """
    _do_change_playback_mode("seek", recording_session, broker, project, seconds)


@app.command()
def stop(
    recording_session: str = typer.Argument(..., help="Recording session id", envvar="REMOTIVE_CLOUD_RECORDING_SESSION"),
    broker: str = typer.Option(None, help="Broker to use"),
    project: str = typer.Option(..., help="Project ID", envvar="REMOTIVE_CLOUD_PROJECT"),
) -> None:
    """
    Stop playing
    """
    _do_change_playback_mode("stop", recording_session, broker, project)


# Copied from signals.py
def read_scripted_code_file(file_path: Path) -> bytes:
    # typer checks that the Path exists
    with open(file_path, "rb") as file:
        return file.read()


@app.command()
def subscribe(  # noqa: PLR0913
    recording_session: str = typer.Argument(..., help="Recording session id", envvar="REMOTIVE_CLOUD_RECORDING_SESSION"),
    broker: str = typer.Option(None, help="Broker to use"),
    signal: List[str] = typer.Option(None, help="Signal names to subscribe to, mandatory when not using script"),
    script: Path = typer.Option(
        None,
        exists=True,
        file_okay=True,
        dir_okay=False,
        writable=False,
        readable=True,
        resolve_path=True,
        help="Supply a path to Lua script that to use for signal transformation",
    ),
    on_change_only: bool = typer.Option(default=False, help="Only get signal if value is changed"),
    project: str = typer.Option(..., help="Project ID", envvar="REMOTIVE_CLOUD_PROJECT"),
) -> None:
    """
    Allows you to subscribe to signals based on a mounted recording without knowing the broker URL.
    This simplifies when playing recordings from the cloud.

    Terminal plotting is not yet supported here so we refer to remotive broker signals subscribe --x-plot for this.
    """
    if script is None:
        if len(signal) == 0:
            print_generic_error("You must use include at least one signal and one namespace or use script when subscribing")
            sys.exit(1)
    if script is not None:
        if len(signal) > 0:
            print_generic_error("You must must not specify --signal when using --script")
            sys.exit(1)

    broker_client = _get_broker_info(project, recording_session, broker, "subscribe")

    try:
        if script is not None:
            script_src = read_scripted_code_file(script)
            broker_client.subscribe_on_script(script_src, lambda sig: print_generic_message(json.dumps(list(sig))), on_change_only)
        else:

            def to_subscribable_signal(sig: str):
                arr = sig.split(":")
                if len(arr) != 2:
                    print_hint(f"--signal must have format namespace:signal ({sig})")
                    sys.exit(1)
                return SubscribableSignal(namespace=arr[0], name=arr[1])

            signals_to_subscribe_to = list(map(to_subscribable_signal, signal))
            broker_client.long_name_subscribe(
                signals_to_subscribe_to, lambda sig: print_generic_message(json.dumps(list(sig))), on_change_only
            )
            print_generic_message("Subscribing to signals, press Ctrl+C to exit")
    except grpc.RpcError as rpc_error:
        print_grpc_error(rpc_error)

    except Exception as e:
        print_generic_error(str(e))
        sys.exit(1)


def _do_change_playback_mode(  # noqa: C901, PLR0913, PLR0912
    mode: str,
    recording_session: str,
    brokerstr: str,
    project: str,
    seconds: int | None = None,
    progress_on_play: bool = False,
    repeat: bool = False,
) -> None:
    response = Rest.handle_get(f"/api/project/{project}/files/recording/{recording_session}", return_response=True)
    if response is None:
        return
    r = json.loads(response.text)
    enabled_recordings: List[Any] = [r for r in r["recordings"] if r["enabled"]]
    files = [{"recording": rec["fileName"], "namespace": rec["metadata"]["namespace"]} for rec in enabled_recordings]

    broker_name = brokerstr if brokerstr is not None else "personal"
    response = Rest.handle_get(f"/api/project/{project}/brokers/{broker_name}", return_response=True, allow_status_codes=[404])
    if response is None:
        return
    if response.status_code == 404:
        broker_arg = ""
        if brokerstr is not None:
            broker_arg = f" --broker {brokerstr} --ensure-broker-started"
        print_generic_error("You need to mount the recording before you play")
        print_hint(f"remotive cloud recordings mount {recording_session}{broker_arg} --project {project}")
        sys.exit(1)

    broker_info = json.loads(response.text)
    broker = Broker(broker_info["url"], None)

    _verify_recording_on_broker(broker, recording_session, mode, project)

    if mode == "pause":
        broker.pause_play(files, True)
    elif mode == "play":
        broker.play(files, True)
        if progress_on_play or repeat:
            _track_progress(broker, repeat, files)
    elif mode == "seek":
        if seconds is not None:
            broker.seek(files, int(seconds * 1000000), True)
        else:
            broker.seek(files, 0, True)
    elif mode == "stop":
        broker.seek(files, 0, True)
    elif mode == "status":
        _track_progress(broker, repeat, files)
    else:
        raise ValueError(f"Illegal command {mode}")


def _track_progress(broker: Broker, repeat: bool, files: List[Any]) -> None:
    p = Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), transient=True)
    t = p.add_task("label", total=1)
    if repeat:
        print_unformatted(":point_right: Keep this command running in terminal to keep the recording play with repeat")
    with p:

        def print_progress(offset: int, total: int, current_mode: str) -> None:
            p.update(
                t,
                description=f"{(datetime.timedelta(seconds=offset))} / {(datetime.timedelta(seconds=total))} ({current_mode})",
            )

        broker.listen_on_playback(repeat, files, print_progress)


def _verify_recording_on_broker(broker: Broker, recording_session: str, mode: str, project: str) -> None:
    try:
        # Here we try to verify that we are operating on a recording that is mounted on the
        # broker so we can verify this before we try playback and can also present some good
        # error messages
        tmp = os.path.join(tempfile.gettempdir(), os.urandom(24).hex())
        broker.download(".cloud.context", tmp, True)
        with open(tmp, "r", encoding="utf8") as f:
            json_context = json.loads(f.read())
            if json_context["recordingSessionId"] != recording_session:
                print_generic_error(
                    f"The recording id mounted is '{json_context['recordingSessionId']}' "
                    f"which not the same as you are trying to {mode}, use cmd below to mount this recording"
                )
                print_hint(f"remotive cloud recordings mount {recording_session} --project {project}")
                sys.exit(1)
    except grpc.RpcError as rpc_error:
        if rpc_error.code() == grpc.StatusCode.NOT_FOUND:
            print_generic_error(f"You must use mount to prepare a recording before you can use {mode}")
            print_hint(f"remotive cloud recordings mount {recording_session} --project {project}")
        else:
            print_grpc_error(rpc_error)
        sys.exit(1)


def _get_broker_info(project: str, recording_session: str, broker: Union[str, None], mode: str) -> Broker:
    # Verify it exists
    Rest.handle_get(f"/api/project/{project}/files/recording/{recording_session}", return_response=True)

    broker_name = broker if broker is not None else "personal"
    response = Rest.handle_get(f"/api/project/{project}/brokers/{broker_name}", return_response=True, allow_status_codes=[404])
    if response is None:
        print_generic_error(f"No response from: /api/project/{project}/brokers/{broker_name}")
        sys.exit(1)
    if response.status_code == 404:
        broker_arg = ""
        if broker is not None:
            broker_arg = f"--broker {broker} --ensure-broker-started"
        print_generic_error("You need to mount the recording before you play")
        print_hint(f"remotive cloud recordings mount {recording_session} {broker_arg} --project {project}")
        sys.exit(1)
    broker_info = json.loads(response.text)
    broker_client = Broker(broker_info["url"], None)
    _verify_recording_on_broker(broker_client, recording_session, mode, project)
    return broker_client
