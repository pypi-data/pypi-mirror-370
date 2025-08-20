from __future__ import annotations

from cli.settings.token_file import TokenFile, TokenFileAccount
from cli.utils.rest_helper import RestHelper


class InvalidTokenError(Exception):
    """Raised when a token is invalid."""


class UnsupportedTokenVersionError(Exception):
    """Raised when a token version is not supported."""


def migrate_legacy_token(token: TokenFile) -> TokenFile:
    """
    Migrate a token from a legacy format to the latest format.

    Args:
        token: The token to migrate.

    Returns:
        TokenFile: The migrated token.

    Raises:
        InvalidTokenError: If the token is invalid.
        UnsupportedTokenVersionError: If the token version is not supported.
    """
    # use a naive approach to compare versions for now
    version = float(token.version)

    # already migrated
    if version >= 1.1:
        return token

    if version == 1.0:
        res = RestHelper.handle_get("/api/whoami", return_response=True, allow_status_codes=[401, 400, 403], access_token=token.token)
        if res.status_code != 200:
            raise InvalidTokenError(f"Token {token.name} is invalid")

        email = res.json()["email"]
        return TokenFile(
            version="1.1",
            type=token.type,
            name=token.name,
            token=token.token,
            created=token.created,
            expires=token.expires,
            account=TokenFileAccount(email=email),
        )

    raise UnsupportedTokenVersionError(f"Unsupported token version: {token.version}")
