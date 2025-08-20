import sys

import typer
from typing_extensions import Annotated

from cli.cloud.storage.copy import copy
from cli.cloud.storage.uri_or_path import UriOrPath
from cli.cloud.storage.uri_or_path import uri as uri_parser
from cli.cloud.uri import URI, InvalidURIError, JoinURIError
from cli.typer import typer_utils
from cli.utils.console import print_hint
from cli.utils.rest_helper import RestHelper as Rest

HELP = """
Manage files ([yellow]Beta feature not available for all customers[/yellow])

Copy file from local to remote storage and vice versa, list and delete files.
"""

app = typer_utils.create_typer(rich_markup_mode="rich", help=HELP)


@app.command(name="ls")
def list_files(
    project: Annotated[str, typer.Option(help="Project ID", envvar="REMOTIVE_CLOUD_PROJECT", show_default=False)],
    uri: Annotated[URI, typer.Argument(help="Remote storage path", parser=URI)] = "rcs://",  # type: ignore
) -> None:
    """
    Listing remote files

    This will list files and directories in project top level directory
    remotive cloud storage ls rcs://

    This will list all files and directories matching the path
    remotive cloud storage ls rcs://fileOrDirectoryPrefix

    This will list all files and directories in the specified directory
    remotive cloud storage ls rcs://fileOrDirectory/
    """
    Rest.handle_get(f"/api/project/{project}/files/storage{uri.path}")


@app.command(name="rm")
def delete_file(
    project: Annotated[str, typer.Option(help="Project ID", envvar="REMOTIVE_CLOUD_PROJECT", show_default=False)],
    uri: Annotated[URI, typer.Argument(help="Remote storage path", parser=URI, show_default=False)],
) -> None:
    """
    [red]Deletes[/red] a file from remote storage, this cannot be undone :fire:

    [white]remotive cloud storage rm rcs://directory/filename[/white]
    """
    Rest.handle_delete(f"/api/project/{project}/files/storage{uri.path}")


@app.command(name="cp")
def copy_file(
    project: Annotated[str, typer.Option(help="Project ID", envvar="REMOTIVE_CLOUD_PROJECT", show_default=False)],
    source: Annotated[UriOrPath, typer.Argument(help="Remote or local path to source file", parser=uri_parser, show_default=False)],
    dest: Annotated[UriOrPath, typer.Argument(help="Remote or local path to destination file", parser=uri_parser, show_default=False)],
    overwrite: Annotated[bool, typer.Option(help="Overwrite existing file on RCS")] = False,
) -> None:
    """
    Copies a file to or from remote storage

    remotive cloud storage cp rcs://dir/filename .
    remotive cloud storage cp rcs://dir/filename filename

    remotive cloud storage cp filename rcs://dir/
    remotive cloud storage cp filename rcs://dir/filename
    """
    try:
        return copy(project=project, source=source.value, dest=dest.value, overwrite=overwrite)
    except (InvalidURIError, JoinURIError, ValueError, FileNotFoundError, FileExistsError) as e:
        print_hint(str(e))
        sys.exit(1)
