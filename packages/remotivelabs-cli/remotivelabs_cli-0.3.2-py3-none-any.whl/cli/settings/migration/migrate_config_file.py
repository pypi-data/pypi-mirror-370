from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Optional

from cli.settings.config_file import ConfigFile, loads
from cli.settings.core import Settings
from cli.settings.migration.migration_tools import get_token_file


def migrate_account_data(config: dict[str, Any], settings: Settings) -> Optional[dict[str, Any]]:
    """
    Migrates Account property credentials_name to credentials_file
    """
    accounts = config.get("accounts", {})
    to_delete = []
    found_old = False
    for account_email, account_info in list(accounts.items()):
        cred_name = account_info.pop("credentials_name", None)
        if not cred_name:
            continue

        # found legacy account, try to migrate it, or drop it...
        found_old = True

        token_file = get_token_file(cred_name, settings.config_dir)
        if not token_file:
            sys.stderr.write(f"Dropping account {account_email!r}: credentials file for {cred_name} not found")
            to_delete.append(account_email)
            continue

        cred_file = token_file.get_token_file_name()
        if not cred_file:
            sys.stderr.write(f"Dropping account {account_email!r}: credentials file for {cred_name} not found")
            to_delete.append(account_email)
            continue

        account_info["credentials_file"] = cred_file

    # actually remove them (also remove active if it was the one being removed)
    for account_email in to_delete:
        del accounts[account_email]
        if config.get("active", None) == account_email:
            config["active"] = None

    return config if found_old else None


def migrate_config_file(path: Path, settings: Settings) -> ConfigFile:
    """
    Migrates data in config file to new format
    """
    data = path.read_text()
    loaded_data: dict[str, Any] = json.loads(data)
    migrated_data = migrate_account_data(loaded_data, settings)
    if not migrated_data:
        return loads(data)

    sys.stderr.write("Migrating old configuration format")
    migrated_config: ConfigFile = ConfigFile.from_dict(migrated_data)
    settings._write_config_file(migrated_config)
    return migrated_config
