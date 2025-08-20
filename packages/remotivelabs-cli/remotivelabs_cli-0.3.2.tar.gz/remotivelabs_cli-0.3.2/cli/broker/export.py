from __future__ import annotations

import signal as os_signal
import sys
from typing import Any, List

import grpc
import typer

from cli.utils.console import print_generic_message, print_grpc_error, print_hint

from ..typer import typer_utils
from .lib.broker import Broker, SubscribableSignal

app = typer_utils.create_typer(
    rich_markup_mode="rich",
    help="""
Export subscribed signals to different formats, currently only InfluxDB line protocol
but more formats will come soon
""",
)


@app.command()
def influxdb(
    url: str = typer.Option(..., help="Broker URL", envvar="REMOTIVE_BROKER_URL"),
    api_key: str = typer.Option(None, help="Cloud Broker API-KEY", envvar="REMOTIVE_BROKER_API_KEY"),
    signal: List[str] = typer.Option(..., help="List of signal names to subscribe to in format namespace:signal_name"),
    on_change_only: bool = typer.Option(default=False, help="Only get signal if value is changed"),
    output: str = typer.Option(None, help="Write results to file, defaults to stdout"),
) -> None:
    """
    Exports subscribed signals to InfluxDB line-protocol, really useful to dump some signals into
    influxdb for offline analysis and insights.

    This is a sample for exporting and importing to InfluxDB using remotive-cli and influx-cli

    Export:
    remotive broker export influxdb --url [URL] --output signals.influx  \\
        --signal vehiclebus:Control.SteeringWheel_Position --signal Control.Accelerator_PedalPosition \\
        --signal vehiclebus:GpsPosition.GPS_Longitude --signal vehiclebus:GpsPosition.GPS_Latitude

    Output:
    Control, namespace:vehiclebus SteeringWheel_Position=1.0,Accelerator_PedalPosition=0,Speed=0 1664787032944374000
    GpsPosition, namespace:vehiclebus GPS_Longitude=12.982076,GPS_Latitude=55.618748 1664787032948256000

    Import:
    influx write --org myorg -b my-bucket -p ns --format=lp  -f signals.influx


    """

    # TODO: file is not properly opened using a context manager
    if output is not None:
        f = open(output, "w")

    def exit_on_ctrlc(_sig: Any, _frame: Any) -> None:
        if output is not None:
            f.close()
        sys.exit(0)

    def per_frame_influx_line_protocol(x: Any) -> None:
        signals = list(x)
        if len(signals) == 0:
            return
        sig: str = signals[0]["name"].rpartition(".")[-1]
        frame = signals[0]["name"].rsplit(".", 1)[0]
        namespace = signals[0]["namespace"]
        signals_str = ",".join(list(map(lambda s: f"{sig}={s['value']}", signals)))
        influx_lp = f"{frame},namespace={namespace} {signals_str} {round(signals[0]['timestamp_us'] * 1000)}"
        if output is not None:
            f.write(f"{influx_lp}\n")
        else:
            # TODO: Use log instead of print for debug information?
            print_generic_message(f"{influx_lp}")

    os_signal.signal(os_signal.SIGINT, exit_on_ctrlc)

    try:

        def to_subscribable_signal(sig: str) -> SubscribableSignal:
            arr = sig.split(":")
            if len(arr) != 2:
                print_hint(f"--signal must have format namespace:signal ({sig})")
                sys.exit(1)

            return SubscribableSignal(namespace=arr[0], name=arr[1])

        signals_to_subscribe_to = list(map(to_subscribable_signal, signal))
        broker = Broker(url, api_key)
        broker.long_name_subscribe(signals_to_subscribe_to, per_frame_influx_line_protocol, on_change_only)
    except grpc.RpcError as rpc_error:
        print_grpc_error(rpc_error)
