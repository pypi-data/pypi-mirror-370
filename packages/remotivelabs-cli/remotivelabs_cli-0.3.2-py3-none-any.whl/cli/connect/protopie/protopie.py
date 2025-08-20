# type: ignore
from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Tuple, Union

import grpc
import socketio
from socketio.exceptions import ConnectionError as SocketIoConnectionError

from cli.broker.lib.broker import SubscribableSignal
from cli.broker.lib.client import BrokerException, Client, SignalIdentifier, SignalsInFrame
from cli.settings import settings
from cli.utils.console import print_generic_error, print_generic_message, print_success, print_unformatted_to_stderr

PP_CONNECT_APP_NAME = "RemotiveBridge"

io = socketio.Client()

_has_received_signal = False
is_connected = False
config_path: Path
x_api_key: str
broker: Any


@io.on("connect")
def on_connect() -> None:
    print_success("Connected to ProtoPie Connect")
    io.emit("ppBridgeApp", {"name": PP_CONNECT_APP_NAME})
    io.emit("PLUGIN_STARTED", {"name": PP_CONNECT_APP_NAME})

    global is_connected  # noqa: PLW0603
    is_connected = True


# TODO - Receive message from ProtoPie connect


def get_signals_and_namespaces(
    config: Union[Path, None] = None, signals_to_subscribe_to: Union[List[SubscribableSignal], None] = None
) -> Tuple[List[str], List[str], Union[Dict[str, str], None]]:
    if config is not None:
        with open(config) as f:
            mapping = json.load(f)
            sub = mapping["subscription"]
            signals = list(sub.keys())
            namespaces = list(map(lambda x: sub[x]["namespace"], signals))
    else:
        if signals_to_subscribe_to is None:
            signals = []
            namespaces = []
        else:
            signals = list(map(lambda s: s.name, signals_to_subscribe_to))
            namespaces = list(map(lambda s: s.namespace, signals_to_subscribe_to))
        sub = None
    return signals, namespaces, sub


def get_signal_name(expression: str, s_name: str) -> str:
    if expression is not None:
        try:
            sig_name = eval(f"s_name.{expression}")
            return str(sig_name)
        except Exception as e:
            print_generic_error(f"Failed to evaluate your python expression {expression}")
            print_unformatted_to_stderr(e)
            # This was the only way I could make this work, exiting on another thread than main
            os._exit(1)
    else:
        return s_name


def _connect_to_broker(
    config: Union[Path, None] = None,
    signals_to_subscribe_to: Union[List[SubscribableSignal], None] = None,
    expression: str = "",
    on_change_only: bool = False,
) -> None:  # noqa: C901
    signals, namespaces, sub = get_signals_and_namespaces(config, signals_to_subscribe_to)

    def on_signals(frame: SignalsInFrame) -> None:
        global _has_received_signal  # noqa: PLW0603
        if not _has_received_signal:
            print_generic_message("Bridge-app is properly receiving signals, you are good to go :thumbsup:")
            _has_received_signal = True

        for s in frame:
            if config and sub is not None:
                sig = sub[s.name()]
                sig = s.name() if "mapTo" not in sig.keys() else sig["mapTo"]
                if isinstance(sig, list):
                    for ss in sig:
                        io.emit("ppMessage", {"messageId": get_signal_name(expression, ss), "value": str(s.value())})
                else:
                    io.emit("ppMessage", {"messageId": get_signal_name(expression, sig), "value": str(s.value())})
            else:
                signal_name = get_signal_name(expression, s.name())
                io.emit("ppMessage", {"messageId": signal_name, "value": str(s.value())})

    grpc_connect(on_signals, signals_to_subscribe_to, on_change_only)


def grpc_connect(
    on_signals: Any, signals_to_subscribe_to: Union[List[SignalIdentifier], None] = None, on_change_only: bool = False
) -> None:
    try:
        print_generic_message("Connecting and subscribing to broker...")
        subscription = None
        client = Client(client_id="cli")
        client.connect(url=broker, api_key=x_api_key)
        client.on_signals = on_signals

        if signals_to_subscribe_to is None:
            # TODO: use logs instead of print?
            print_generic_error("No signals to subscribe to")
            return
        subscription = client.subscribe(signals_to_subscribe_to=signals_to_subscribe_to, changed_values_only=on_change_only)
        print_generic_message("Subscription to broker completed")
        print_generic_message("Waiting for signals...")

        while True:
            time.sleep(1)

    except grpc.RpcError as e:
        print_generic_error("Problems connecting or subscribing")
        if isinstance(e, grpc.Call):
            print_generic_error(f"{e.code()} - {e.details()}")
        else:
            print_generic_error(e)

    except BrokerException as e:
        print_generic_error(e)
        if subscription is not None:
            subscription.cancel()

    except KeyboardInterrupt:
        print_generic_message("Keyboard interrupt received. Closing subscription.")
        if subscription is not None:
            subscription.cancel()

    except Exception as e:
        print_generic_error(e)


def do_connect(  # noqa: PLR0913
    address: str,
    broker_url: str,
    api_key: Union[str, None],
    config: Union[Path, None],
    signals: List[SubscribableSignal],
    expression: Union[str, None],
    on_change_only: bool = False,
) -> None:
    global broker  # noqa: PLW0603
    global x_api_key  # noqa: PLW0603
    global config_path  # noqa: PLW0603
    broker = broker_url

    if broker_url.startswith("https"):
        if api_key is None:
            print_generic_message("No --api-key, reading token from file")
            x_api_key = settings.get_active_token_secret()
        else:
            x_api_key = api_key
    elif api_key is not None:
        x_api_key = api_key
    try:
        io.connect(address)
        config_path = config
        while is_connected is None:
            time.sleep(1)
        _connect_to_broker(signals_to_subscribe_to=signals, config=config, expression=expression, on_change_only=on_change_only)
    except SocketIoConnectionError as e:
        print_generic_error("Failed to connect to ProtoPie Connect")
        print_unformatted_to_stderr(e)
        sys.exit(1)
    except Exception as e:
        print_generic_error("Unexpected error")
        print_unformatted_to_stderr(e)
        sys.exit(1)
