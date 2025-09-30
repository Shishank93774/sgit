from .base import GitObject
from typing import Any


class GitBlob(GitObject):
    """Git object representing a blob (file content)."""

    fmt: bytes = b'blob'

    def serialize(self) -> Any:
        """
        Serialize the blob object.

        Returns:
            The raw data of the blob.
        """
        return self.blobdata

    def deserialize(self, data: Any) -> None:
        """
        Populate the blob object from raw data.

        Args:
            data: Raw bytes or string representing the blob content.
        """
        self.blobdata = data
