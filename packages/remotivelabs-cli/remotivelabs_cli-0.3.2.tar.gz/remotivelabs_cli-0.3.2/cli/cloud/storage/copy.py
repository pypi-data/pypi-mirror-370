from __future__ import annotations

import json
from pathlib import Path

from cli.cloud.resumable_upload import upload_signed_url
from cli.cloud.uri import URI
from cli.utils.console import print_success
from cli.utils.rest_helper import RestHelper as Rest

_RCS_STORAGE_PATH = "/api/project/{project}/files/storage{path}"


def copy(project: str, source: URI | Path, dest: URI | Path, overwrite: bool = False) -> None:
    if isinstance(source, Path) and isinstance(dest, Path):
        raise ValueError("Either source or destination must be an rcs:// uri")

    if isinstance(source, URI) and isinstance(dest, URI):
        raise ValueError("Either source or destination must be a local path")

    if isinstance(source, URI) and isinstance(dest, Path):
        _download(source=source, dest=dest, project=project, overwrite=overwrite)

    elif isinstance(source, Path) and isinstance(dest, URI):
        _upload(source=source, dest=dest, project=project, overwrite=overwrite)

    else:
        raise ValueError("invalid copy operation")


def _upload(source: Path, dest: URI, project: str, overwrite: bool = False) -> None:
    if not source.exists():
        raise FileNotFoundError(f"Source file does not exist: {source}")

    files_to_upload = _list_files_for_upload(source, dest)

    for file_path, target_uri in files_to_upload:
        _upload_single_file(file_path, target_uri, project, overwrite)


def _list_files_for_upload(source: Path, dest: URI) -> list[tuple[Path, URI]]:
    upload_pairs = []

    if source.is_dir():
        for file_path in source.rglob("*"):
            if file_path.is_file():
                relative_path = file_path.relative_to(source)
                target_uri = dest / relative_path
                upload_pairs.append((file_path, target_uri))
    else:
        target_uri = dest / source.name if dest.is_dir() else dest
        upload_pairs.append((source, target_uri))

    return upload_pairs


def _upload_single_file(source: Path, target_uri: URI, project: str, overwrite: bool = False) -> None:
    target = _RCS_STORAGE_PATH.format(project=project, path=target_uri.path)
    upload_options = {"overwrite": "always" if overwrite else "never"}
    res = Rest.handle_post(target, return_response=True, body=json.dumps(upload_options))

    json_res = res.json()
    url = json_res["url"]
    headers = json_res["headers"]
    upload_signed_url(url, source, headers)

    print_success(f"Uploaded {source} to {target_uri.path}")


def _download(source: URI, dest: Path, project: str, overwrite: bool = False) -> None:
    if dest.is_dir():
        if not dest.exists():
            raise FileNotFoundError(f"Destination directory {dest} does not exist")
        # create a target file name if destination is a dir
        dest = dest / source.filename

    elif not dest.parent.is_dir() or not dest.parent.exists():
        raise FileNotFoundError(f"Destination directory {dest.parent} does not exist")

    if dest.exists() and not overwrite:
        raise FileExistsError(f"Destination file {dest} already exists")

    target = _RCS_STORAGE_PATH.format(project=project, path=source.path) + "?download=true"
    res = Rest.handle_get(target, return_response=True)

    Rest.download_file(save_file_name=dest.absolute(), url=res.text)
