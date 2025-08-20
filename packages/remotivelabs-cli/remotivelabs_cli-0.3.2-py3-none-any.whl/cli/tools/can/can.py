from pathlib import Path

import can
import typer

from cli.typer import typer_utils
from cli.utils.console import print_generic_error, print_success

HELP = """
CAN related tools
"""

app = typer_utils.create_typer(help=HELP)


@app.command("convert")
def convert(
    in_file: Path = typer.Argument(
        exists=True,
        file_okay=True,
        dir_okay=False,
        writable=False,
        readable=True,
        resolve_path=True,
        help="File to convert from (.blf .asc .log)",
    ),
    out_file: Path = typer.Argument(
        exists=False,
        file_okay=True,
        dir_okay=False,
        writable=True,
        readable=True,
        resolve_path=True,
        help="File to convert to (.blf .asc .log)",
    ),
) -> None:
    r"""
    Converts between ASC, BLF and LOG files. Files must end with .asc, .blf or .log.

    remotive tools can convert \[my_file.blf|.log|.asc] \[my_file.blf|.log|.asc]
    """

    with can.LogReader(in_file, relative_timestamp=False) as reader:
        try:
            with can.Logger(out_file) as writer:
                for msg in reader:
                    writer.on_message_received(msg)
        except Exception as e:
            print_generic_error(f"Failed to convert file: {e}")


@app.command("validate")
def validate(
    in_file: Path = typer.Argument(
        exists=True,
        file_okay=True,
        dir_okay=False,
        writable=False,
        readable=True,
        resolve_path=True,
        help="File to validate (.blf .asc .log)",
    ),
    print_to_terminal: bool = typer.Option(False, help="Print file contents to terminal"),
) -> None:
    r"""
    Validates that the input file is an ASC, BLF and LOG file

    remotive tools can validate \[my_file.blf|.log|.asc]
    """
    with can.LogReader(in_file, relative_timestamp=False) as reader:
        try:
            with can.Printer() as writer:
                for msg in reader:
                    if print_to_terminal:
                        writer.on_message_received(msg)
            print_success(f"{in_file} verified")
        except Exception as e:
            print_generic_error(f"Failed to convert file: {e}")
