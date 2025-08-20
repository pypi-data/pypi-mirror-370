from __future__ import annotations

import sys
from string import Template
from typing import List

import typer

from cli.typer import typer_utils
from cli.utils.console import print_generic_message, print_hint

app = typer_utils.create_typer(
    rich_markup_mode="rich",
    help="""
[Experimental] - Generate template lua script for input and output signals
""",
)


def write(signal_name: str, script: str) -> None:
    path = f"{signal_name}.lua"
    with open(path, "w") as f:
        f.write(script)
    print_generic_message(f"Secret token written to {path}")


@app.command("new-script")
def new_script(
    input_signal: List[str] = typer.Option(..., help="Required input signal names"),
    output_signal: str = typer.Option(..., help="Name of output signal"),
    save: bool = typer.Option(False, help="Save file to disk - Default stored as __output_signal__.lua"),
) -> None:
    def to_subscribable_signal(sig: str) -> tuple[str, str]:
        arr = sig.split(":")
        if len(arr) != 2:
            print_hint(f"--input-signal must have format namespace:signal ({sig})")
            sys.exit(1)
        return arr[0], arr[1]

    signals_to_subscribe_to = list(map(to_subscribable_signal, input_signal))

    def to_local_signal(sig_name: tuple[str, str]) -> str:
        t = Template(
            """
    {
        name = "$sig_name",
        namespace = "$namespace"
    }"""
        )
        return t.substitute(sig_name=sig_name[1], namespace=sig_name[0])

    local_signals = ",".join(list(map(to_local_signal, signals_to_subscribe_to)))

    def to_subscribe_pattern(sig_name: tuple[str, str]) -> str:
        t = Template(
            """
    if (signals["$sig_name"] ~= nil) then
        return return_value_or_bytes(signals["$sig_name"])
    end
    """
        )
        return t.substitute(sig_name=sig_name[1])

    subscribe_pattern = "".join(list(map(to_subscribe_pattern, signals_to_subscribe_to)))

    template = Template(
        """
--
-- Docs available at https://docs.remotivelabs.com/docs/remotive-broker/scripted_signals
--

local local_signals = {$local_signals
}

-- Required, declare which input is needed to operate this program.
function input_signals()
    return local_signals
end

-- Provided parameters are used for populating metadata when listing signals.
function output_signal()
    return "$output_signal"
end

-- Required, declare what frequency you like to get "timer" invoked. 0 means no calls to "timer".
function timer_frequency_hz()
    return 0
end

-- Invoked with the frequency returned by "timer_frequency_hz".
-- @param system_timestamp_us: system time stamp
function timer(system_timestamp_us)
    return return_value_or_bytes("your value")
end

-- Invoked when ANY signal declared in "local_signals" arrive
-- @param signals_timestamp_us: signal time stamp
-- @param system_timestamp_us
-- @param signals: array of signals containing all or a subset of signals declared in "local_signals". Make sure to nil check before use.
function signals(signals, namespace, signals_timestamp_us, system_timestamp_us)
    -- TODO - replace this code with what you want todo

    $subscribe_pattern
    return return_nothing()
end

-- helper return function, make sure to use return_value_or_bytes or return_nothing.
function return_value_or_bytes(value_or_bytes)
    return value_or_bytes
end

-- helper return function, make sure to use return_value_or_bytes or return_nothing.
function return_nothing()
    return
end

"""
    )

    script = template.substitute(
        local_signals=local_signals,
        subscribe_pattern=subscribe_pattern,
        output_signal=output_signal,
    )

    if save:
        write(output_signal, script)
    else:
        print_generic_message(script)
