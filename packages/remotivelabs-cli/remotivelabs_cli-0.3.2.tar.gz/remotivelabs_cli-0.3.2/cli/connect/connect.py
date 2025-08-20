from __future__ import annotations

import json
import sys
from pathlib import Path

import typer
from typing_extensions import List

from cli.broker.lib.broker import SubscribableSignal
from cli.typer import typer_utils
from cli.utils.console import print_hint

from .protopie import protopie as ppie

app = typer_utils.create_typer()


@app.command()
def protopie(  # noqa: PLR0913
    config: Path = typer.Option(
        None,
        exists=True,
        file_okay=True,
        dir_okay=False,
        writable=False,
        readable=True,
        resolve_path=True,
        help="Configuration file with signal subscriptions and mapping if needed",
    ),
    signal: List[str] = typer.Option([], help="Signal names to subscribe to, mandatory when not using script"),
    signal_name_expression: str = typer.Option(
        None, help='[Experimental] Python expression to rename signal names, i.e \'lower().replace(".","_")\''
    ),
    changed_values_only: bool = typer.Option(
        True, help="Only receive signal when its value is changed to minimize amount of data received"
    ),
    broker_url: str = typer.Option(..., help="Broker URL", envvar="REMOTIVE_BROKER_URL"),
    api_key: str = typer.Option(None, help="Cloud Broker API-KEY", envvar="REMOTIVE_BROKER_API_KEY"),
    pp_connect_host: str = typer.Option("http://localhost:9981", help="ProtoPie Connect URL"),
) -> None:
    """
    ProtoPie Connect bridge-app to connect signals with RemotiveBroker

    Subscribe to signals and send signal values to your Pie in a simple way. You can subscribe to signals from command line
    using --signal or use --config to use a json configuration file.

    ```
    $ remotive connect protopie --signal vss:Vehicle.Chassis.SteeringWheel.Angle --signal vss:Vehicle.Speed
    ```

    You can use a configuration file for this if you have many signals, want to share the configuration or you want
    custom mapping of the signal name.
    ```
    $ remotive connect protopie --config my-protopie-config.json
    ```

    Sample my-protopie-config.json
    ```
    {
      "subscription": {
        "Vehicle.CurrentLocation.Heading": {
          "namespace": "vss"
        },
        "Vehicle.Speed": {
          "namespace": "vss",
           "mapTo": ["Speed", "VehicleSpeed"]
        }
      }
    }
    ```
    For simple changes to signal names its possible to use a simple python expression that will be applied to all signal
    names before its published to ProtoPie connect, i.e replacing chars or substring to match variables in Pie. This is
    intended for simple use cases when you do not have a configuration file, otherwise we recommend using the mapTo
    field in the configuration.

    This will replace all occurrences of . (dot) with _ (underscore)
        ```
    $ remotive connect protopie --signal vss:Vehicle.Chassis.SteeringWheel.Angle --signal-name-expression 'replace(".", "_")'
    ```
    """

    if len(signal) > 0 and config is not None:
        print_hint("You must choose either --signal or --config, not both")
        sys.exit(1)

    if len(signal) == 0 and config is None:
        print_hint("You must choose either --signal or --config")
        sys.exit(1)

    def to_subscribable_signal(sig: str) -> SubscribableSignal:
        arr = sig.split(":")

        if len(arr) != 2:
            print_hint(f"--signal must have format namespace:signal ({sig})")
            sys.exit(1)

        return SubscribableSignal(namespace=arr[0], name=arr[1])

    if len(signal) > 0:
        signals_to_subscribe_to = list(map(to_subscribable_signal, signal))
    else:
        with open(config, "r", encoding="utf8") as f:
            c = json.load(f)
            s = c["subscription"]
            ss = []
            for entry in s.keys():
                ss.append(SubscribableSignal(namespace=s[entry]["namespace"], name=entry))
        signals_to_subscribe_to = ss

    ppie.do_connect(  # type: ignore
        address=pp_connect_host,
        broker_url=broker_url,
        api_key=api_key,
        expression=signal_name_expression,
        config=config,
        signals=signals_to_subscribe_to,
        on_change_only=changed_values_only,
    )
