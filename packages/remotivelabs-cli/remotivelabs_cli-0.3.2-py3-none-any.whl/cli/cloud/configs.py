import os.path
import shutil
from pathlib import Path

import requests
import typer
from rich.progress import Progress, SpinnerColumn, TextColumn

from cli.typer import typer_utils
from cli.utils.console import print_generic_error, print_success
from cli.utils.rest_helper import RestHelper as Rest

app = typer_utils.create_typer()


@app.command("list")
def list_signal_databases(project: str = typer.Option(..., help="Project ID", envvar="REMOTIVE_CLOUD_PROJECT")) -> None:
    """
    List available signal databases in project
    """
    Rest.handle_get(f"/api/project/{project}/files/config")


@app.command("delete")
def delete(
    signal_db_file: str = typer.Argument("", help="Signal database file"),
    project: str = typer.Option(..., help="Project ID", envvar="REMOTIVE_CLOUD_PROJECT"),
) -> None:
    """
    Deletes the specified signal database
    """
    Rest.handle_delete(f"/api/project/{project}/files/config/{signal_db_file}")


@app.command()
def upload(
    path: Path = typer.Argument(
        ...,
        exists=True,
        file_okay=True,
        dir_okay=False,
        writable=False,
        readable=True,
        resolve_path=True,
        help="Path to signal database file to upload",
    ),
    project: str = typer.Option(..., help="Project ID", envvar="REMOTIVE_CLOUD_PROJECT"),
) -> None:
    """
    Uploads signal database to project
    """
    res_text = Rest.handle_put(url=f"/api/project/{project}/files/config/{os.path.basename(path)}/uploadfile", return_response=True)
    if res_text is not None:
        res_json = res_text.json()
        Rest.upload_file_with_signed_url(
            path=path,
            url=res_json["url"],
            upload_headers={"Content-Type": "application/octet-stream"},
            progress_label=f"Uploading {path}...",
        )


@app.command()
def describe(
    signal_db_file: str = typer.Argument("", help="Signal database file"),
    project: str = typer.Option(..., help="Project ID", envvar="REMOTIVE_CLOUD_PROJECT"),
) -> None:
    """
    Shows all metadata related to this signal database
    """
    Rest.handle_get(f"/api/project/{project}/files/config/{signal_db_file}")


@app.command()
def download(
    signal_db_file: str = typer.Argument("", help="Signal database file"),
    project: str = typer.Option(..., help="Project ID", envvar="REMOTIVE_CLOUD_PROJECT"),
) -> None:
    """
    Downloads the specified signal database to disk
    """
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        Rest.ensure_auth_token()

        progress.add_task(description=f"Downloading {signal_db_file}", total=None)

        # First request the download url from cloud. This is a public signed url that is valid
        # for a short period of time
        get_signed_url_resp = requests.get(
            f"{Rest.get_base_url()}/api/project/{project}/files/config/{signal_db_file}/download",
            headers=Rest.get_headers(),
            allow_redirects=True,
            timeout=60,
        )
        if get_signed_url_resp.status_code == 200:
            # Next download the actual file
            download_resp = requests.get(url=get_signed_url_resp.text, stream=True, timeout=60)
            if download_resp.status_code == 200:
                with open(signal_db_file, "wb") as out_file:
                    shutil.copyfileobj(download_resp.raw, out_file)
                print_success(f"{signal_db_file} downloaded")
            else:
                print_generic_error(f"Got unexpected status {download_resp.status_code}")
        else:
            print_generic_error(f"Got unexpected status {get_signed_url_resp.status_code}\n")
