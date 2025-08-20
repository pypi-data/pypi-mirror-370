from __future__ import annotations

import os

import typer

from cli.broker.discovery import discover as discover_cmd
from cli.typer import typer_utils

from . import export, files, licenses, playback, record, scripting, signals

app = typer_utils.create_typer(rich_markup_mode="rich")


# TODO: remove this?
def cb(url: str = typer.Option(None, is_eager=False, help="Broker URL", envvar="REMOTIVE_BROKER_URL")) -> None:
    # This can be used to override the --url per command, lets see if this is a better approach
    if url is not None:
        os.environ["REMOTIVE_BROKER_URL"] = url


# TODO: move broker commands to subcommand instead?
app.command(help="Discover brokers on this network")(discover_cmd)
app.callback()(cb)

# subcommands
app.add_typer(playback.app, name="playback", help="Manage playing recordings")
app.add_typer(record.app, name="record", help="Record data on buses")
app.add_typer(files.app, name="files", help="Upload/Download configurations and recordings")
app.add_typer(signals.app, name="signals", help="Find and subscribe to signals")
app.add_typer(export.app, name="export", help="Export to external formats")
app.add_typer(scripting.app, name="scripting", help="LUA scripting utilities")
app.add_typer(licenses.app, name="license", help="View and request license to broker")

if __name__ == "__main__":
    app()
