from __future__ import annotations

from itertools import chain
from pathlib import Path

from cli.settings.token_file import TokenFile
from cli.utils.console import print_generic_message


def list_token_files(config_dir: Path) -> list[TokenFile]:
    """
    List all token files in the config directory

    Note! Dont use settings, as that will couple settings to the old config and token formats we want to migrate away from.
    """
    token_files = []
    patterns = ["personal-token-*.json", "service-account-token-*.json"]
    files = list(chain.from_iterable(config_dir.glob(pattern) for pattern in patterns))
    for file in files:
        try:
            token_file = TokenFile.from_json_str(file.read_text())
            token_files.append(token_file)
        except Exception:
            print_generic_message(f"warning: invalid token file {file}. Consider removing it.")
    return token_files


def get_token_file(cred_name: str, config_dir: Path) -> TokenFile | None:
    """
    Get the token file for a given credentials name.

    Note! Dont use settings, as that will couple settings to the old config and token formats we want to migrate away from.
    """
    token_files = list_token_files(config_dir)
    matches = [token_file for token_file in token_files if token_file.name == cred_name]
    if len(matches) != 1:
        return None
    return matches[0]
