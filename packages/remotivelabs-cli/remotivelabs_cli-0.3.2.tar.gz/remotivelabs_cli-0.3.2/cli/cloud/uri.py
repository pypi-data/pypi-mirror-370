from __future__ import annotations

from os import PathLike
from pathlib import PurePosixPath
from urllib.parse import urlparse


class InvalidURIError(Exception):
    """Raised when an invalid URI is encountered"""


class JoinURIError(Exception):
    """Raised when an error occurs while joining URIs"""


class URI:
    """
    Custom type for rcs (Remotive Cloud Storage) URIs.

    The URI format follows the pattern: rcs://bucket/path/to/resource
    """

    scheme: str
    """The URI scheme (default: 'rcs')"""

    path: str
    """The full path component, including leading slash"""

    filename: str
    """The name of the file or last path segment"""

    bucket: str
    """The first path segment after the leading slash"""

    parent: URI
    """The parent URI. If at root, returns a copy of itself."""

    def __init__(self, value: str, scheme: str = "rcs"):
        """
        Create a new URI.

        Args:
            value: The URI string in format "scheme://path/to/resource"
            scheme: The URI scheme (default: 'rcs')

        Raises:
            InvalidURIError: If the URI format is invalid
        """
        self._raw = value
        self.scheme = scheme

        parsed = urlparse(value)
        if parsed.scheme != self.scheme:
            raise InvalidURIError(f"Invalid URI scheme. Expected '{self.scheme}://', got '{parsed.scheme}://'")
        if parsed.netloc.startswith((".", "-", "#", " ", "/", "\\")):
            raise InvalidURIError(f"Invalid URI. Path cannot start with invalid characters: '{value}'")
        if not parsed.netloc and parsed.path == "/":
            raise InvalidURIError(f"Invalid URI: '{value}'")

        self.path = f"/{parsed.netloc}{parsed.path}" if parsed.netloc else f"/{parsed.path}"

        self._posix_path = PurePosixPath(self.path)
        self.filename = self._posix_path.name
        self.bucket = self._posix_path.parts[1] if len(self._posix_path.parts) > 1 else ""

        if self._posix_path == PurePosixPath("/"):
            self.parent = self
        else:
            parent_path = self._posix_path.parent
            new_uri = f"{self.scheme}://{str(parent_path)[1:]}"
            self.parent = URI(new_uri, scheme=self.scheme)

    def is_dir(self) -> bool:
        """Check if the URI points to a directory."""
        return self.path.endswith("/")

    def __truediv__(self, other: PathLike[str] | str) -> URI:
        """
        Join this URI with another path component.

        Args:
            other: Path component to join

        Returns:
            A new URI with the joined path

        Raises:
            JoinURIError: If trying to join an absolute path
            TypeError: If the path component is not a string or PathLike
        """
        if str(other).startswith("/"):
            raise JoinURIError(f"Cannot join absolute path '{other}' to URI")

        is_dir = str(other).endswith("/")
        new_path = self._posix_path / other

        for part in new_path.parts:
            if part == "..":
                new_path = new_path.parent
            elif part != ".":
                new_path = new_path / part

        new_uri = f"{self.scheme}://{new_path.relative_to('/')}"  # we need to strip the starting '/'
        new_uri = new_uri if not is_dir else f"{new_uri}/"  # and append slash if the added path was a dir
        return URI(new_uri, scheme=self.scheme)

    def __str__(self) -> str:
        """Return the original URI string."""
        return self._raw

    def __repr__(self) -> str:
        """Return the original URI string."""
        return f"URI({self._raw})"
