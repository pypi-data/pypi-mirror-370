from __future__ import annotations

from pathlib import Path

from cli.cloud.uri import URI, InvalidURIError


def uri(path: str) -> UriOrPath:
    """
    Parses a path and returns a UriOrPath object.

    NOTE: The name of this function is important as it is used by Typer to determine the name/type of the argument
    """
    try:
        p: Path | URI = URI(path)
    except InvalidURIError:
        p = Path(path)
    return UriOrPath(p)


class UriOrPath:
    """
    Union type for handling local and remote paths for Remotive Cloud Storage

    Note: This custom type only exists because Typer currently does not support union types
    TODO: Move to commands package when refactored
    """

    def __init__(self, value: Path | URI) -> None:
        self._value = value

    @property
    def uri(self) -> URI | None:
        return self._value if isinstance(self._value, URI) else None

    @property
    def path(self) -> Path | None:
        return self._value if isinstance(self._value, Path) else None

    @property
    def value(self) -> Path | URI:
        return self._value

    def __str__(self) -> str:
        return str(self._value)
