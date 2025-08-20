from __future__ import annotations

import re
from datetime import date, datetime
from typing import Any, Literal

from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator

from cli.utils.time import parse_date

DEFAULT_EMAIL = "unknown@remotivecloud.com"
PERSONAL_TOKEN_FILE_PREFIX = "personal-token-"
SERVICE_ACCOUNT_TOKEN_FILE_PREFIX = "service-account-token-"

TokenType = Literal["authorized_user", "service_account"]


def _email_to_safe_filename(email: str) -> str:
    """Replace any invalid character with an underscore"""
    return re.sub(r'[<>:"/\\|?*]', "_", email)


def _parse_token_type(token: str) -> TokenType:
    if token.startswith("pa"):
        return "authorized_user"
    if token.startswith("sa"):
        return "service_account"
    raise ValueError(f"Unknown token type for token: {token}")


class TokenFileAccount(BaseModel):
    """
    TokenFileAccount represents the account information for a token file.
    """

    email: EmailStr = DEFAULT_EMAIL


class TokenFile(BaseModel):
    """
    TokenFile represents a token file for the CLI.

    TODO: Should all setters return a new instance of the TokenFile?
    """

    version: str = "1.0"
    type: TokenType
    name: str
    token: str
    created: date
    expires: date
    account: TokenFileAccount = Field(default_factory=TokenFileAccount)

    @field_validator("created", "expires", mode="before")
    @classmethod
    def _validate_parse_date(cls, value: str | date) -> date:
        if isinstance(value, date):
            return value
        return parse_date(value)

    @model_validator(mode="before")
    @classmethod
    def _validate_json_data(cls, json_data: Any) -> Any:
        """
        Try to migrate old formats and missing fields as best we can.

        NOTE: If we ever need to add a new version (like 2.0), we should add explicit classes for each version (e.g. TokenFileV1,
        TokenFileV2, etc.), each with their own fields. This will allow us to migrate to new versions without breaking
        backwards compatibility.
        """
        if not isinstance(json_data, dict):
            return json_data

        if "version" not in json_data:
            json_data["version"] = "1.0"

        if "type" not in json_data and "token" in json_data:
            json_data["type"] = _parse_token_type(json_data["token"])

        if "account" not in json_data:
            json_data["account"] = {"email": DEFAULT_EMAIL}
        elif isinstance(json_data["account"], str):
            json_data["account"] = {"email": json_data["account"]}

        return json_data

    def get_token_file_name(self) -> str:
        """
        Returns the name of the token_file following a predictable naming format.
        """
        email = _email_to_safe_filename(self.account.email) if self.account is not None else "unknown"
        if self.type == "authorized_user":
            return f"{PERSONAL_TOKEN_FILE_PREFIX}{self.name}-{email}.json"
        return f"{SERVICE_ACCOUNT_TOKEN_FILE_PREFIX}{self.name}-{email}.json"

    def is_expired(self) -> bool:
        return datetime.today().date() > self.expires

    def expires_in_days(self) -> int:
        return (self.expires - datetime.today().date()).days

    @classmethod
    def from_json_str(cls, data: str) -> TokenFile:
        return cls.model_validate_json(data)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> TokenFile:
        return cls.model_validate(data)

    def to_json_str(self) -> str:
        return self.model_dump_json()

    def to_dict(self) -> dict[str, Any]:
        return self.model_dump()


def loads(data: str) -> TokenFile:
    """
    Creates a TokenFile from a JSON string.
    """
    return TokenFile.from_json_str(data)


def dumps(token_file: TokenFile) -> str:
    """
    Returns the JSON string representation of the TokenFile.
    """
    return token_file.to_json_str()
