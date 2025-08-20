from __future__ import annotations

from cli.settings.core import Settings
from cli.settings.migration.migrate_token_file import InvalidTokenError, UnsupportedTokenVersionError, migrate_legacy_token
from cli.settings.migration.migration_tools import list_token_files
from cli.settings.token_file import TokenFile, dumps

ACTIVE_TOKEN_FILE_NAME = "cloud.secret.token"


def migrate_legacy_tokens(tokens: list[TokenFile]) -> tuple[list[TokenFile], set[str]]:
    """
    Determine which tokens can be updated and which should be removed.

    Returns:
        tuple of (updated_tokens, invalid_tokens)
    """
    updated_tokens: list[TokenFile] = []
    invalid_tokens: set[str] = set()

    for token in tokens:
        try:
            migrated_token = migrate_legacy_token(token)
            if migrated_token.version != token.version:
                updated_tokens.append(migrated_token)
        except (InvalidTokenError, UnsupportedTokenVersionError):
            # Token not valid or unsupported version, mark for removal
            invalid_tokens.add(token.name)

    return updated_tokens, invalid_tokens


def _write_updated_tokens(settings: Settings, updated_tokens: list[TokenFile]) -> None:
    for updated_token in updated_tokens:
        settings.remove_token_file(name=updated_token.name)
        if updated_token.type == "authorized_user":
            settings.add_personal_token(dumps(updated_token), overwrite_if_exists=True)
        elif updated_token.type == "service_account":
            settings.add_service_account_token(dumps(updated_token))
        else:
            raise ValueError(f"Unsupported token type: {updated_token.type}")


def _remove_invalid_tokens(settings: Settings, invalid_tokens: set[str]) -> None:
    for token_name in invalid_tokens:
        settings.remove_token_file(name=token_name)


def _remove_old_secret_file(settings: Settings) -> bool:
    old_activated_secret_file = settings.config_dir / ACTIVE_TOKEN_FILE_NAME
    old_secret_exists = old_activated_secret_file.exists()
    if old_secret_exists:
        old_activated_secret_file.unlink(missing_ok=True)
    return old_secret_exists


def migrate_any_legacy_tokens(settings: Settings) -> bool:
    """
    Migrate any legacy tokens to the latest TokenFile format.

    If the legacy secret file exists (cloud.secret.token), it will be removed.

    Returns True if any tokens were migrated, False otherwise.
    """
    tokens = list_token_files(settings.config_dir)

    # Get tokens to update/remove
    updated_tokens, invalid_tokens = migrate_legacy_tokens(tokens)

    # Perform file operations
    _write_updated_tokens(settings, updated_tokens)
    _remove_invalid_tokens(settings, invalid_tokens)

    # Remove old secret file if exists
    old_secret_removed = _remove_old_secret_file(settings)
    if old_secret_removed:
        return True  # We migrated at least one token

    # only return True if we migrated at least one token
    return len(updated_tokens) + len(invalid_tokens) > 0
