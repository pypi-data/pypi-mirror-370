import glob
import json
import os
import re
import sys
import tempfile
import time
import urllib.parse
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union
from urllib.parse import quote

import grpc
import requests
import typer
from rich.progress import Progress, SpinnerColumn, TaskID, TextColumn, track
from typing_extensions import Annotated

from cli.cloud.uri import URI
from cli.typer import typer_utils
from cli.utils.console import (
    print_generic_error,
    print_generic_message,
    print_grpc_error,
    print_hint,
    print_success,
    print_unformatted,
    print_unformatted_to_stderr,
)
from cli.utils.rest_helper import RestHelper as Rest

from ..broker.lib.broker import Broker
from .recordings_playback import app as playback_app

app = typer_utils.create_typer()
app.add_typer(playback_app, name="playback")


def uid(p: Any) -> Any:
    # TODO: use log instead of print for debug information?
    print_generic_message(p)
    return p["uid"]


# ruff: noqa: FA100
# ruff: noqa: C901


@app.command("list")
def list_recordings(
    is_processing: bool = typer.Option(default=False, help="Use this option to see only those that are beeing processed or are invalid"),
    project: str = typer.Option(..., help="Project ID", envvar="REMOTIVE_CLOUD_PROJECT"),
) -> None:
    """
    List all recording sessions in a project. You can choose to see all valid recordings (default) or use
    --is-processing and you will get those that are currently beeing processed or that failed to be validated.
    """

    if is_processing:
        res = Rest.handle_get(f"/api/project/{project}/files/recording/processing", return_response=True)
        json_res: List[Dict[str, Any]] = res.json()
        print_generic_message(json.dumps(list(filter(lambda r: r["status"] == "RUNNING" or r["status"] == "FAILED", json_res))))
    else:
        Rest.handle_get(f"/api/project/{project}/files/recording")


@app.command(help="Shows details about a specific recording in project")
def describe(
    recording_session: str = typer.Argument(..., help="Recording session id", envvar="REMOTIVE_CLOUD_RECORDING_SESSION"),
    project: str = typer.Option(..., help="Project ID", envvar="REMOTIVE_CLOUD_PROJECT"),
) -> None:
    Rest.handle_get(f"/api/project/{project}/files/recording/{recording_session}")


@app.command(name="import")
def import_as_recording(
    uri: Annotated[URI, typer.Argument(help="Remote storage path", parser=URI, show_default=False)],
    project: str = typer.Option(..., help="Project ID", envvar="REMOTIVE_CLOUD_PROJECT"),
) -> None:
    """
    Imports a file from Storage as a recording.

    NOTE that Storage is not yet available to all customers
    """
    Rest.handle_post(
        url=f"/api/project/{project}/files/recording",
        return_response=True,
        progress_label=f"Importing {uri.path}...",
        body=json.dumps({"path": uri.path}),
    )

    print_hint(f"Import started, you can track progress with 'remotive cloud recordings list --is-processing --project {project}'")


def do_start(name: str, project: str, api_key: str, return_response: bool = False) -> requests.Response:
    body = {"size": "S"}
    if not api_key:
        body["apiKey"] = api_key

    return Rest.handle_post(
        f"/api/project/{project}/brokers/{name}",
        body=json.dumps(body),
        return_response=return_response,
        progress_label=f"Starting {name}...",
    )


@app.command(help="Prepares all recording files and transformations to be available for playback")
def mount(  # noqa: C901
    recording_session: str = typer.Argument(..., help="Recording session id", envvar="REMOTIVE_CLOUD_RECORDING_SESSION"),
    broker: Optional[str] = typer.Option(None, help="Broker to use"),
    ensure_broker_started: bool = typer.Option(default=False, help="Ensure broker exists, start otherwise"),
    transformation_name: str = typer.Option("default", help="Specify a custom signal transformation to use"),
    project: str = typer.Option(..., help="Project ID", envvar="REMOTIVE_CLOUD_PROJECT"),
) -> None:
    Rest.ensure_auth_token()

    Rest.handle_get(f"/api/project/{project}/files/recording/{recording_session}", return_response=True)

    if broker is None:
        r = Rest.handle_get(url=f"/api/project/{project}/brokers/personal", return_response=True, allow_status_codes=[404])

        if r.status_code == 200:
            broker_info = r.json()
            broker = broker_info["shortName"]
        elif r.status_code == 404:
            r = do_start("personal", project, "", return_response=True)
            if r.status_code != 200:
                print_generic_error(r.text)
                sys.exit(0)
        else:
            print_generic_error(f"Got http status code {r.status_code}")
            raise typer.Exit(0)
    else:
        r = Rest.handle_get(url=f"/api/project/{project}/brokers/{broker}", return_response=True, allow_status_codes=[404])

        if r.status_code == 404:
            if ensure_broker_started:
                r = do_start(broker, project, "", return_response=True)
                if r.status_code != 200:
                    print_generic_error(r.text)
                    sys.exit(1)
            else:
                print_generic_error(f"Broker {broker} not running")
                sys.exit(1)
        elif r.status_code != 200:
            sys.stderr.write(f"Got http status code {r.status_code}")
            raise typer.Exit(1)

    broker_info = r.json()
    broker = broker_info["shortName"]
    broker_config_query = ""
    if transformation_name != "default":
        broker_config_query = f"?brokerConfigName={transformation_name}"

    Rest.handle_get(
        f"/api/project/{project}/files/recording/{recording_session}/upload{broker_config_query}",
        params={"brokerName": broker},
        return_response=True,
        progress_label="Preparing recording on broker...",
    )
    print_unformatted_to_stderr("Successfully mounted recording on broker")
    print_unformatted(json.dumps(broker_info))


@app.command(help="Downloads the specified recording file to disk")
def download_recording_file(
    recording_file_name: str = typer.Argument(..., help="Recording file to download"),
    recording_session: str = typer.Option(
        ..., help="Recording session id that this file belongs to", envvar="REMOTIVE_CLOUD_RECORDING_SESSION"
    ),
    project: str = typer.Option(..., help="Project ID", envvar="REMOTIVE_CLOUD_PROJECT"),
) -> None:
    Rest.ensure_auth_token()
    recording_file_name_qouted = quote(recording_file_name, safe="")
    get_signed_url_resp = requests.get(
        f"{Rest.get_base_url()}/api/project/{project}/files/recording/{recording_session}/recording-file/{recording_file_name_qouted}",
        headers=Rest.get_headers(),
        allow_redirects=True,
        timeout=60,
    )
    if get_signed_url_resp.status_code == 200:
        # Next download the actual file
        Rest.download_file(Path(recording_file_name), get_signed_url_resp.json()["downloadUrl"])
        print_success(f"Downloaded {recording_file_name}")
    else:
        print_generic_error(get_signed_url_resp.text)


@app.command(name="delete")
def delete(
    recording_session: str = typer.Argument(..., help="Recording session id", envvar="REMOTIVE_CLOUD_RECORDING_SESSION"),
    project: str = typer.Option(..., help="Project ID", envvar="REMOTIVE_CLOUD_PROJECT"),
) -> None:
    """
    Deletes the specified recording session including all media files and configurations.

    """
    Rest.handle_delete(f"/api/project/{project}/files/recording/{recording_session}")


@app.command(name="delete-recording-file")
def delete_recording_file(
    recording_file_name: str = typer.Argument(..., help="Recording file to download"),
    recording_session: str = typer.Option(
        ..., help="Recording session id that this file belongs to", envvar="REMOTIVE_CLOUD_RECORDING_SESSION"
    ),
    project: str = typer.Option(..., help="Project ID", envvar="REMOTIVE_CLOUD_PROJECT"),
) -> None:
    """
    Deletes the specified recording file

    """
    Rest.handle_delete(f"/api/project/{project}/files/recording/{recording_session}/recording-file/{recording_file_name}")


@app.command()
def upload(  # noqa: C901, PLR0912, PLR0915
    path: Path = typer.Argument(
        ...,
        exists=True,
        file_okay=True,
        dir_okay=False,
        writable=False,
        readable=True,
        resolve_path=True,
        help="Path to recording file to upload",
    ),
    project: str = typer.Option(..., help="Project ID", envvar="REMOTIVE_CLOUD_PROJECT"),
    recording_session: Optional[str] = typer.Option(default=None, help="Optional existing recording to upload file to"),
) -> None:
    """
    Uploads a recording to RemotiveCloud.
    Except for recordings from RemotiveBroker you can also upload Can ASC (.asc), Can BLF(.blf) and  Can LOG (.log, .txt)
    """

    filename = os.path.basename(path.name)
    Rest.ensure_auth_token()

    if recording_session is None:
        r = Rest.handle_post(f"/api/project/{project}/files/recording/{filename}", return_response=True)
    else:
        r = Rest.handle_post(f"/api/project/{project}/files/recording/{recording_session}/recording-file/{filename}", return_response=True)
    if r is None:
        return

    upload_url = r.text
    url_path = urllib.parse.urlparse(upload_url).path
    # Upload_id is the first part of the path
    match = re.match(r"^/([^/]+)/organisation/(.*)$", url_path)
    if match:
        upload_id = match.group(1)
    else:
        print_generic_error("Something went wrong, please try again. Please contact RemotiveLabs support if this problem remains")
        print_hint("Please make sure to use the latest version of RemotiveCLI")
        sys.exit(1)

    upload_response = Rest.upload_file_with_signed_url(
        path=path, url=upload_url, upload_headers={"Content-Type": "application/x-www-form-urlencoded"}, return_response=True
    )

    if upload_response is None:
        return

    # Exact same as in cloud console
    def get_processing_message(step: str) -> str:  # noqa: PLR0911
        if step == "REQUESTED":
            return "Preparing file..."
        if step == "VALIDATING":
            return "Validating file..."
        if step == "CONVERT":
            return "Converting file..."
        if step == "SPLIT":
            return "Splitting file..."
        if step == "ZIP":
            return "Compressing file..."
        if step == "FINALIZE":
            return "Finishing up..."
        return "Processing..."

    if 200 <= upload_response.status_code < 300:
        # We need to print the error message outside the with Progress so the indicator is closed
        error_message: Union[str, None] = None
        with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), transient=True) as p:
            t = p.add_task("Processing...", total=1)
            while True:
                time.sleep(1)
                r = Rest.handle_get(
                    f"/api/project/{project}/files/recording/processing", return_response=True, use_progress_indicator=False
                )
                if r is None:
                    return
                status_list: List[Dict[str, Any]] = r.json()
                res = list(filter(lambda s: s["uploadId"] == upload_id, status_list))
                if len(res) == 1:
                    tracking_state = res[0]
                    if tracking_state["status"] != "FAILED" and tracking_state["status"] != "SUCCESS":
                        p.update(task_id=t, description=get_processing_message(tracking_state["step"]))
                    else:
                        if tracking_state["status"] == "FAILED":
                            error_message = f"Processing of uploaded file failed: {tracking_state['errors'][0]['message']}"
                        else:
                            print_success("File successfully uploaded")
                        break
                else:
                    error_message = "Something went wrong, please try again. Please contact RemotiveLabs support if this problem remains"
                    break
        if error_message is not None:
            print_generic_error(error_message)
            sys.exit(1)

    else:
        print_generic_error(f"Got status code: {upload_response.status_code} {upload_response.text}")


# TODO - Change to use Path for directory
@app.command()
def upload_broker_configuration(
    directory: Path = typer.Argument(
        ...,
        exists=True,
        file_okay=False,
        dir_okay=True,
        writable=False,
        readable=True,
        resolve_path=True,
        help="Directory to upload",
    ),
    recording_session: str = typer.Option(..., help="Recording session id", envvar="REMOTIVE_CLOUD_RECORDING_SESSION"),
    project: str = typer.Option(..., help="Project ID", envvar="REMOTIVE_CLOUD_PROJECT"),
    overwrite: bool = typer.Option(False, help="Overwrite existing configuration if it exists"),
) -> None:
    """
    Uploads a broker configuration directory
    """
    # Must end with /

    #
    # List files in specified directory. Look for interfaces.json and use that directory where this is located
    # as configuration home directory
    #
    files = list(filter(lambda item: "interfaces.json" in item, glob.iglob(str(directory) + "/**/**", recursive=True)))
    if len(files) == 0:
        sys.stderr.write("No interfaces.json found in directory, this file is required")
        raise typer.Exit(1)
    if len(files) > 1:
        sys.stderr.write(f"{len(files)} interfaces.json found in directoryw which is not supported")
        raise typer.Exit(1)
    broker_config_dir_name = os.path.dirname(files[0]).rsplit("/", 1)[-1]

    #
    # Get the current details about broker configurations to see if a config with this
    # name already exists
    #
    # task = progress.add_task(description=f"Preparing upload of {broker_config_dir_name}", total=1)
    details_resp = Rest.handle_get(f"/api/project/{project}/files/recording/{recording_session}", return_response=True)
    if details_resp is None:
        return
    details = details_resp.json()
    existing_configs = details["brokerConfigurations"]
    if len(existing_configs) > 0:
        data = list(filter(lambda x: x["name"] == broker_config_dir_name, existing_configs))
        if len(data) > 0:
            if overwrite:
                Rest.handle_delete(
                    f"/api/project/{project}/files/recording/{recording_session}/configuration/{broker_config_dir_name}", quiet=True
                )
            else:
                sys.stderr.write("Broker configuration already exists, use --overwrite to replace\n")
                raise typer.Exit(1)

    #
    # From the list of files, create a tuple of local_path to the actual file
    # and a remote path as it should be stored in cloud
    #
    file_infos = list(
        map(
            lambda item: {"local_path": item, "remote_path": f"/{broker_config_dir_name}{item.rsplit(broker_config_dir_name, 1)[-1]}"},
            glob.iglob(str(directory) + "/**/*.*", recursive=True),
        )
    )

    #
    # convert this remote paths and ask cloud to prepare upload urls for those
    #
    json_request_upload_urls_req = {"name": "not_used", "paths": list(map(lambda x: x["remote_path"], file_infos))}

    response = Rest.handle_put(
        url=f"/api/project/{project}/files/recording/{recording_session}/configuration",
        return_response=True,
        body=json.dumps(json_request_upload_urls_req),
    )
    if response is None:
        return
    if response.status_code != 200:
        print_generic_error(f"Failed to prepare configuration upload: {response.text} - {response.status_code}")
        raise typer.Exit(1)

    #
    # Upload urls is a  remote_path : upload_url dict
    # '/my_config/interfaces.json' : "<upload_url>"
    #
    upload_urls = json.loads(response.text)

    # For each file - upload
    for file in track(file_infos, description="Uploading..."):
        key = file["remote_path"]
        path = file["local_path"]
        url = upload_urls[key]
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        r = requests.put(url, open(path, "rb"), headers=headers, timeout=60)
        if r.status_code != 200:
            print_generic_error(f"Failed to upload broker configuration: {r.text} - {r.status_code}")
            raise typer.Exit(1)

    print_success(f"Uploaded broker configuration {broker_config_dir_name}")


@app.command(help="Downloads the specified broker configuration directory as zip file")
def download_broker_configuration(
    broker_config_name: str = typer.Argument(..., help="Broker config name"),
    recording_session: str = typer.Option(..., help="Recording session id", envvar="REMOTIVE_CLOUD_RECORDING_SESSION"),
    project: str = typer.Option(..., help="Project ID", envvar="REMOTIVE_CLOUD_PROJECT"),
) -> None:
    Rest.ensure_auth_token()
    r = Rest.handle_get(
        url=f"/api/project/{project}/files/recording/{recording_session}/configuration/{broker_config_name}", return_response=True
    )
    if r is None:
        return
    filename = get_filename_from_cd(r.headers.get("content-disposition"))
    if filename is not None:
        with open(filename, "wb") as f:
            f.write(r.content)
        print_success(f"Downloaded file {filename}")


@app.command(help="Delete the specified broker configuration")
def delete_broker_configuration(
    broker_config_name: str = typer.Argument(..., help="Broker config name"),
    recording_session: str = typer.Option(..., help="Recording session id", envvar="REMOTIVE_CLOUD_RECORDING_SESSION"),
    project: str = typer.Option(..., help="Project ID", envvar="REMOTIVE_CLOUD_PROJECT"),
) -> None:
    Rest.handle_delete(url=f"/api/project/{project}/files/recording/{recording_session}/configuration/{broker_config_name}")


@app.command(help="Copy recording to another project")
def copy(
    recording_session: str = typer.Argument(..., help="Recording session id"),
    from_project: str = typer.Option(..., help="Source project"),
    to_project: str = typer.Option(..., help="Destination project"),
) -> None:
    Rest.handle_post(
        url=f"/api/project/{from_project}/files/recording/{recording_session}/copy", body=json.dumps({"projectUid": to_project})
    )


@app.command(deprecated=True)
def play(
    recording_session: str = typer.Argument(..., help="Recording session id", envvar="REMOTIVE_CLOUD_RECORDING_SESSION"),
    broker: str = typer.Option(None, help="Broker to use"),
    project: str = typer.Option(..., help="Project ID", envvar="REMOTIVE_CLOUD_PROJECT"),
) -> None:
    """
    Plays a recording (Deprecated - Use recordings playback play)"
    """
    _do_change_playback_mode("play", recording_session, broker, project)


@app.command(deprecated=True)
def pause(
    recording_session: str = typer.Argument(..., help="Recording session id", envvar="REMOTIVE_CLOUD_RECORDING_SESSION"),
    broker: str = typer.Option(None, help="Broker to use"),
    project: str = typer.Option(..., help="Project ID", envvar="REMOTIVE_CLOUD_PROJECT"),
) -> None:
    """
    Pause recording (Deprecated - Use recordings playback pause")
    """
    _do_change_playback_mode("pause", recording_session, broker, project)


@app.command(deprecated=True)
def seek(
    recording_session: str = typer.Argument(..., help="Recording session id", envvar="REMOTIVE_CLOUD_RECORDING_SESSION"),
    seconds: int = typer.Option(..., min=0, help="Target offset in seconds"),
    broker: str = typer.Option(None, help="Broker to use"),
    project: str = typer.Option(..., help="Project ID", envvar="REMOTIVE_CLOUD_PROJECT"),
) -> None:
    """
    Seek into recording (Deprecated - Use recordings playback seek)
    """
    _do_change_playback_mode("seek", recording_session, broker, project, seconds)


@app.command(deprecated=True)
def stop(
    recording_session: str = typer.Argument(..., help="Recording session id", envvar="REMOTIVE_CLOUD_RECORDING_SESSION"),
    broker: str = typer.Option(None, help="Broker to use"),
    project: str = typer.Option(..., help="Project ID", envvar="REMOTIVE_CLOUD_PROJECT"),
) -> None:
    """
    Stop recording (Deprecated - Use recordings playback stop)
    """
    _do_change_playback_mode("stop", recording_session, broker, project)


def _do_change_playback_mode(  # noqa: PLR0912
    mode: str, recording_session: str, broker_name: Optional[str], project: str, seconds: Optional[int] = None
) -> None:
    response = Rest.handle_get(f"/api/project/{project}/files/recording/{recording_session}", return_response=True)
    if response is None:
        return
    r = json.loads(response.text)
    recordings: List[Any] = r["recordings"]
    files = list(map(lambda rec: {"recording": rec["fileName"], "namespace": rec["metadata"]["namespace"]}, recordings))

    if broker_name is not None:
        response = Rest.handle_get(f"/api/project/{project}/brokers/{broker_name}", return_response=True, allow_status_codes=[404])
    else:
        response = Rest.handle_get(f"/api/project/{project}/brokers/personal", return_response=True, allow_status_codes=[404])
    if response is None:
        return
    if response.status_code == 404:
        broker_arg = ""
        if broker_name is not None:
            broker_arg = f" --broker {broker_name} --ensure-broker-started"
        print_generic_error("You need to mount the recording before you play")
        print_hint(f"remotive cloud recordings mount {recording_session}{broker_arg} --project {project}")
        sys.exit(1)

    broker_info = json.loads(response.text)
    broker = Broker(broker_info["url"], None)
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
        print_grpc_error(rpc_error)
        sys.exit(1)
    if mode == "pause":
        broker.pause_play(files, True)
    elif mode == "play":
        r = broker.play(files, True)
    elif mode == "seek":
        if seconds is not None:
            broker.seek(files, int(seconds * 1000000), True)
        else:
            broker.seek(files, 0, True)
    elif mode == "stop":
        broker.seek(files, 0, True)
    else:
        raise ValueError(f"Illegal command {mode}")


def get_filename_from_cd(cd: Union[str, None]) -> Union[str, None]:
    """
    Get filename from content-disposition
    """
    if not cd:
        return None
    fname = re.findall("filename=(.+)", cd)
    if len(fname) == 0:
        return None
    return str(fname[0])


def use_progress(label: str) -> Tuple[Progress, TaskID]:
    p = Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), transient=True)
    t = p.add_task(label, total=1)
    return (p, t)
