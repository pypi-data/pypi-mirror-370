from __future__ import annotations

from typing import Any, Optional

from pydantic import BaseModel, Field, model_validator

from cli.settings.token_file import TokenFile


class Account(BaseModel):
    """
    Account represents an account in the configuration file.

    TODO: Add email field to Account
    """

    credentials_file: str
    default_organization: Optional[str] = None


class ConfigFile(BaseModel):
    """
    ConfigFile represents the configuration file for the CLI.

    TODO: Should all setters return a new instance of the ConfigFile?
    """

    version: str = "1.0"
    active: Optional[str] = None
    accounts: dict[str, Account] = Field(default_factory=dict)

    @model_validator(mode="before")
    @classmethod
    def _validate_json_data(cls, json_data: Any) -> Any:
        """Try to migrate old formats and missing fields as best we can."""
        if not isinstance(json_data, dict):
            return json_data

        # If the active account is not in accounts, remove it
        if "active" in json_data and json_data["active"] not in json_data["accounts"]:
            del json_data["active"]

        return json_data

    def get_active_account(self) -> Optional[Account]:
        if not self.active:
            return None
        account = self.get_account(self.active)
        if not account:
            raise KeyError(f"Activated account {self.active} is not a valid account")
        return account

    def activate_account(self, email: str) -> None:
        account = self.get_account(email)
        if not account:
            raise KeyError(f"Account {email} does not exists")
        self.active = email

    def _update_account(self, email: str, **updates: Any) -> None:
        """TODO: Consider using model_copy and always return a new instance of ConfigFile"""
        existing_account = self.get_account(email)
        if existing_account:
            updated_account = existing_account.model_copy(update=updates)
        else:
            updated_account = Account(**updates)

        new_accounts = {**self.accounts, email: updated_account}
        self.accounts = new_accounts

    def init_account(self, email: str, token_file: TokenFile) -> None:
        """
        Create a new account with the given email and token file.
        """
        self._update_account(email, credentials_file=token_file.get_token_file_name())

    def set_default_organization_for_account(self, email: str, default_organization: Optional[str] = None) -> None:
        if not self.get_account(email):
            raise KeyError(f"Account with email {email} has not been initialized with token")
        self._update_account(email, default_organization=default_organization)

    def get_account(self, email: str) -> Optional[Account]:
        return self.accounts.get(email)

    def remove_account(self, email: str) -> None:
        self.accounts.pop(email, None)

    @classmethod
    def from_json_str(cls, data: str) -> ConfigFile:
        return cls.model_validate_json(data)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ConfigFile:
        return cls.model_validate(data)

    def to_json_str(self) -> str:
        return self.model_dump_json()

    def to_dict(self) -> dict[str, Any]:
        return self.model_dump()


def loads(data: str) -> ConfigFile:
    """
    Creates a ConfigFile from a JSON string.
    """
    return ConfigFile.from_json_str(data)


def dumps(config: ConfigFile) -> str:
    """
    Returns the JSON string representation of the ConfigFile.
    """
    return config.to_json_str()
