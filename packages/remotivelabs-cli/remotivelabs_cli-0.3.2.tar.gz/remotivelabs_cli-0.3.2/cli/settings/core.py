from __future__ import annotations

import os
import stat
import sys
from pathlib import Path
from typing import Optional

from rich.console import Console

from cli.settings import config_file as cf
from cli.settings import state_file as sf
from cli.settings import token_file as tf
from cli.settings.config_file import Account, ConfigFile
from cli.settings.state_file import StateFile
from cli.settings.token_file import TokenFile
from cli.utils.console import print_hint

err_console = Console(stderr=True)

CONFIG_DIR_PATH = Path.home() / ".config" / "remotive"
CLI_CONFIG_FILE_NAME = "config.json"
CLI_INTERNAL_STATE_FILE_NAME = "app-state.json"


class InvalidSettingsFilePathError(Exception):
    """Raised when trying to access an invalid settings file or file path"""


class Settings:
    """
    Settings handles tokens and other config for the remotive CLI

    TODO: migrate away from singleton instance
    TODO: How do we handle REMOTIVE_CLOUD_ACCESS_TOKEN in combination with active account? What takes precedence?
    """

    config_dir: Path

    def __init__(self, config_dir: Path) -> None:
        self.config_dir = config_dir
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.config_file_path = self.config_dir / CLI_CONFIG_FILE_NAME
        if not self.config_file_path.exists():
            self._write_config_file(ConfigFile())
        self.state_dir = self.config_dir / "state"
        self.state_file_path = self.state_dir / CLI_INTERNAL_STATE_FILE_NAME
        if not self.state_file_path.exists():
            self._write_state_file(StateFile())

    def _get_cli_config(self) -> ConfigFile:
        return self._read_config_file()

    def _get_state_file(self) -> StateFile:
        return self._read_state_file()

    def should_perform_update_check(self) -> bool:
        """
        Check if we should perform an update check.
        """
        return self._get_state_file().should_perform_update_check()

    def set_default_organisation(self, organisation: str) -> None:
        """
        Set the default organization for the active account

        TODO: Raise error, dont sys.exit
        """
        config = self._get_cli_config()
        active_account = config.get_active_account()
        if not active_account:
            print_hint("You must have an account activated in order to set default organization")
            sys.exit(1)
        active_account.default_organization = organisation
        self._write_config_file(config)

    def get_active_account(self) -> Account | None:
        """
        Get the current active account

        TODO: Add email field to Account
        """
        return self._get_cli_config().get_active_account()

    def get_active_token_file(self) -> TokenFile | None:
        """
        Get the token file for the current active account
        """
        active_account = self.get_active_account()
        return self._read_token_file(active_account.credentials_file) if active_account else None

    def get_active_token(self) -> str | None:
        """
        Get the token secret for the current active account
        """
        token_file = self.get_active_token_file()
        return token_file.token if token_file else None

    def activate_token(self, token_file: TokenFile) -> TokenFile:
        """
        Activate a token by name or path

        The token secret will be set as the current active secret.

        Returns the activated token file
        """
        config = self._get_cli_config()
        config.activate_account(token_file.account.email)
        self._write_config_file(config)
        return token_file

    def is_active_account(self, email: str) -> bool:
        """
        Returns True if the given email is the active account
        """
        return self._get_cli_config().active == email

    def clear_active_account(self) -> None:
        """
        Clear the current active token
        """
        config = self._get_cli_config()
        config.active = None
        self._write_config_file(config)

    def get_token_file_by_email(self, email: str) -> Optional[TokenFile]:
        """
        Get a token file by email.

        If multiple tokens are found, the first one is returned.
        """
        accounts = self._get_cli_config().accounts.get(email)
        return self._read_token_file(accounts.credentials_file) if accounts else None

    def get_token_file(self, name: str) -> TokenFile | None:
        """
        Get a token file by name or path
        """
        # 1. Try relative path
        if (self.config_dir / name).exists():
            return self._read_token_file(name)

        # 2. Try name
        return self._get_token_by_name(name)

    def remove_token_file(self, name: str) -> None:
        """
        Remove a token file by name or path
        """
        token_file = self.get_token_file(name)
        if not token_file:
            return

        # If the token is active, clear it first
        email = token_file.account.email
        if self.is_active_account(email):
            self.clear_active_account()

        # Remove the token file
        path = self.config_dir / self._get_cli_config().accounts[email].credentials_file
        path.unlink()

        # Remove the account from the config file
        config = self._get_cli_config()
        config.remove_account(email)
        self._write_config_file(config)

    def add_personal_token(self, token: str, activate: bool = False, overwrite_if_exists: bool = False) -> TokenFile:
        """
        Add a personal token
        """
        token_file = tf.loads(token)
        if token_file.type != "authorized_user":
            raise ValueError("Token type MUST be authorized_user")

        token_file = self.add_token_as_account(token_file, overwrite_if_exists)

        if activate:
            self.activate_token(token_file)

        return token_file

    def add_service_account_token(self, token: str, overwrite_if_exists: bool = False) -> TokenFile:
        """
        Add a service account token
        """
        token_file = tf.loads(token)
        if token_file.type != "service_account":
            raise ValueError("Token type MUST be service_account")

        return self.add_token_as_account(token_file, overwrite_if_exists)

    def add_token_as_account(self, token_file: TokenFile, overwrite_if_exists: bool = False) -> TokenFile:
        """
        Add an account to the config file
        """
        file_name = token_file.get_token_file_name()
        path = self.config_dir / file_name
        if path.exists() and not overwrite_if_exists:
            raise FileExistsError(f"Token file already exists: {path}")

        self._write_token_file(path, token_file)
        cli_config = self._get_cli_config()
        cli_config.init_account(email=token_file.account.email, token_file=token_file)
        self._write_config_file(cli_config)

        return token_file

    def list_accounts(self) -> dict[str, Account]:
        """
        List all accounts
        """
        return self._get_cli_config().accounts

    def list_personal_accounts(self) -> dict[str, Account]:
        """
        List all personal accounts

        TODO: add account type to Account
        """
        accounts = self.list_accounts()
        return {
            email: account
            for email, account in accounts.items()
            if self._read_token_file(account.credentials_file).type == "authorized_user"
        }

    def list_service_accounts(self) -> dict[str, Account]:
        """
        List all personal accounts

        TODO: add account type to Account
        """
        accounts = self.list_accounts()
        return {
            email: account
            for email, account in accounts.items()
            if self._read_token_file(account.credentials_file).type == "service_account"
        }

    def list_token_files(self) -> list[TokenFile]:
        """
        List all token files
        """
        accounts = self._get_cli_config().accounts.values()
        return [self._read_token_file(account.credentials_file) for account in accounts]

    def list_personal_token_files(self) -> list[TokenFile]:
        """
        List all personal token files
        """
        return [token_file for token_file in self.list_token_files() if token_file.type == "authorized_user"]

    def list_service_account_token_files(self) -> list[TokenFile]:
        """
        List all service account token files
        """
        return [token_file for token_file in self.list_token_files() if token_file.type == "service_account"]

    def set_last_update_check_time(self, timestamp: str) -> None:
        """
        Sets the timestamp of the last self update check
        """
        state = self._read_state_file()
        state.last_update_check_time = timestamp
        self._write_state_file(state)

    def _get_token_by_name(self, name: str) -> TokenFile | None:
        """
        Token name is only available as a property of TokenFile, so we must iterate over all tokens to find the right one
        """
        token_files = self.list_token_files()
        matches = [token_file for token_file in token_files if token_file.name == name]
        if len(matches) != 1:
            return None
        return matches[0]

    def _read_token_file(self, file_name: str) -> TokenFile:
        path = self.config_dir / file_name
        data = self._read_file(path)
        return tf.loads(data)

    def _write_token_file(self, path: Path, token: TokenFile) -> Path:
        data = tf.dumps(token)
        return self._write_file(path, data)

    def _read_config_file(self) -> ConfigFile:
        data = self._read_file(self.config_file_path)
        return cf.loads(data)

    def _write_config_file(self, config: ConfigFile) -> Path:
        data = cf.dumps(config)
        return self._write_file(self.config_file_path, data)

    def _read_state_file(self) -> StateFile:
        data = self._read_file(self.state_file_path)
        return sf.loads(data)

    def _write_state_file(self, state: StateFile) -> Path:
        data = sf.dumps(state)
        return self._write_file(self.state_file_path, data)

    def _read_file(self, path: Path) -> str:
        if not path.exists():
            raise FileNotFoundError(f"File could not be found: {path}")
        return path.read_text(encoding="utf-8")

    def _write_file(self, path: Path, data: str) -> Path:
        if self.config_dir not in path.parents:
            raise InvalidSettingsFilePathError(f"file {path} not in settings dir {self.config_dir}")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(data, encoding="utf8")
        os.chmod(path, stat.S_IRUSR | stat.S_IWUSR)
        return path


settings = Settings(CONFIG_DIR_PATH)
"""
Global/module-level settings instance. Module-level variables are only loaded once, at import time.

TODO: Migrate away from singleton instance
"""
