from __future__ import annotations

import json
import numbers
import os
import signal as os_signal
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable, List, TypedDict, Union

import grpc
import plotext as plt  # type: ignore
import typer

from cli.typer import typer_utils
from cli.utils.console import print_generic_error, print_generic_message, print_grpc_error, print_hint

from .lib.broker import Broker, SubscribableSignal

app = typer_utils.create_typer(help=help)

DEFAULT_GRPC_URL = "http://localhost:50051"


class Signals(TypedDict):
    name: str
    signals: List[Any]


signal_values: Dict[Any, Any] = {}


@app.command(name="list")
def list_signals(
    url: str = typer.Option(DEFAULT_GRPC_URL, help="Broker URL", envvar="REMOTIVE_BROKER_URL"),
    api_key: str = typer.Option(None, help="Cloud Broker API-KEY or access token", envvar="REMOTIVE_BROKER_API_KEY"),
    name_starts_with: Union[str, None] = typer.Option(None, help="Signal name prefix to include"),
    name_ends_with: Union[str, None] = typer.Option(None, help="Signal name suffix to include"),
) -> None:
    """
    List signal metadata on a broker

    Filter are inclusive so --name-starts-with and --name-ends-with will include name that matches both
    """
    try:
        broker = Broker(url, api_key)
        available_signals = broker.list_signal_names(prefix=name_starts_with, suffix=name_ends_with)
        print_generic_message(json.dumps(available_signals))
    except grpc.RpcError as rpc_error:
        print_grpc_error(rpc_error)


def read_scripted_code_file(file_path: Path) -> bytes:
    try:
        print_generic_message(str(file_path))
        with open(file_path, "rb") as file:
            return file.read()
    except FileNotFoundError:
        print_generic_error("File not found. Please check your file path.")
        sys.exit(1)


@app.command()
def subscribe(  # noqa: C901, PLR0913, PLR0915
    url: str = typer.Option(DEFAULT_GRPC_URL, help="Broker URL", envvar="REMOTIVE_BROKER_URL"),
    api_key: str = typer.Option(None, help="Cloud Broker API-KEY or access token", envvar="REMOTIVE_BROKER_API_KEY"),
    signal: List[str] = typer.Option([], help="Signal names to subscribe to, mandatory when not using script"),
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
    x_plot: bool = typer.Option(default=False, help="Experimental: Plot the signal in terminal. Note graphs are not aligned by time"),
    x_plot_size: int = typer.Option(default=100, help="Experimental: how many points show for each plot"),
    # samples: int = typer.Option(default=0, he)
) -> None:
    """
    Subscribe to a selection of signals

    Subscribe to two signals and have it printed to terminal
    ```
    remotive broker signals subscribe  --url http://localhost:50051 --signal can1:signal1 --signal can0:signal2
    ```

    Subscribe using a LUA script with signal transformations, read more about scripted signals at https://docs.remotivelabs.com/docs/remotive-broker
    ```
    remotive broker signals subscribe  --url http://localhost:50051 --script myvss_script.lua
    ```
    """

    if script is None:
        if len(signal) == 0:
            print_generic_error("You must use --signal or use --script when subscribing")
            sys.exit(1)

    if script is not None:
        if len(signal) > 0:
            print_generic_error("You must must not specify --signal when using --script")
            sys.exit(1)

    plt.title("Signals")

    def exit_on_ctrlc(_sig: Any, _frame: Any) -> None:
        os._exit(0)

    def on_frame_plot(x: Iterable[Any]) -> None:
        plt.clt()  # to clear the terminal
        plt.cld()  # to clear the data only
        frames = list(x)
        plt.clf()
        plt.subplots(len(list(filter(lambda n: n.startswith("ts_"), signal_values.keys()))))
        plt.theme("pro")

        for frame in frames:
            name = frame["name"]

            if not isinstance(frame["value"], numbers.Number):
                # Skip non numberic values
                # TODO - would exit and print info message if I knew how to
                continue

            y = [frame["value"]]
            t = [frame["timestamp_us"]]

            if name not in signal_values:
                signal_values[name] = [None] * x_plot_size
                signal_values[f"ts_{name}"] = [None] * x_plot_size
            signal_values[name] = signal_values[name] + y
            signal_values[f"ts_{name}"] = signal_values[f"ts_{name}"] + t

            if len(signal_values[name]) > x_plot_size:
                signal_values[name] = signal_values[name][len(signal_values[name]) - x_plot_size :]

            if len(signal_values[f"ts_{name}"]) > x_plot_size:
                signal_values[f"ts_{name}"] = signal_values[f"ts_{name}"][len(signal_values[f"ts_{name}"]) - x_plot_size :]

        cnt = 1
        for key, value in signal_values.items():
            if not key.startswith("ts_"):
                plt.subplot(cnt, 1).plot(signal_values[f"ts_{key}"], value, label=key, color=cnt)
                cnt = cnt + 1
        plt.sleep(0.001)  # to add
        plt.show()

    def on_frame_print(x: Iterable[Any]) -> None:
        # TODO: use log instead of print for debug information?
        print_generic_message(json.dumps(list(x)))

    os_signal.signal(os_signal.SIGINT, exit_on_ctrlc)

    if x_plot:
        on_frame_func = on_frame_plot
    else:
        on_frame_func = on_frame_print

    try:
        if script is not None:
            script_src = read_scripted_code_file(script)
            broker = Broker(url, api_key)
            broker.subscribe_on_script(script_src, on_frame_func, on_change_only)
        else:

            def to_subscribable_signal(sig: str):
                arr = sig.split(":")
                if len(arr) != 2:
                    print_hint(f"--signal must have format namespace:signal ({sig})")
                    sys.exit(1)
                return SubscribableSignal(namespace=arr[0], name=arr[1])

            signals_to_subscribe_to = list(map(to_subscribable_signal, signal))

            broker = Broker(url, api_key)
            broker.long_name_subscribe(signals_to_subscribe_to, on_frame_func, on_change_only)
        print_generic_message("Subscribing to signals, press Ctrl+C to exit")
    except grpc.RpcError as rpc_error:
        print_grpc_error(rpc_error)


@app.command(help="List namespaces on broker")
def namespaces(
    url: str = typer.Option(DEFAULT_GRPC_URL, help="Broker URL", envvar="REMOTIVE_BROKER_URL"),
    api_key: str = typer.Option(None, help="Cloud Broker API-KEY or access token", envvar="REMOTIVE_BROKER_API_KEY"),
) -> None:
    try:
        broker = Broker(url, api_key)
        namespaces_json = broker.list_namespaces()
        print_generic_message(json.dumps(namespaces_json))
    except grpc.RpcError as rpc_error:
        print_grpc_error(rpc_error)


@app.command()
def frame_distribution(
    url: str = typer.Option(..., help="Broker URL", envvar="REMOTIVE_BROKER_URL"),
    api_key: str = typer.Option(None, help="Cloud Broker API-KEY or access token", envvar="REMOTIVE_BROKER_API_KEY"),
    namespace: str = typer.Option(..., help="Namespace"),
) -> None:
    """
    Use this command to get frames currently available on the specified namespace.
    """
    try:
        broker = Broker(url, api_key)

        def on_data(data: Dict[str, Any]) -> None:
            timestamp: str = datetime.now().strftime("%H:%M:%S")
            distribution = data["countsByFrameId"]
            if len(distribution) == 0:
                print_hint(f"{timestamp} - No frames available")
            else:
                for d in distribution:
                    print_generic_message(f"{timestamp}: {d}")

        broker.listen_on_frame_distribution(namespace, on_data)
    except grpc.RpcError as rpc_error:
        print_grpc_error(rpc_error)
