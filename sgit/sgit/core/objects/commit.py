from .base import GitObject
from typing import Any, Dict


class GitCommit(GitObject):
    """Git object representing a commit."""

    fmt: bytes = b'commit'

    def serialize(self) -> bytes:
        """
        Serialize the commit object to raw bytes.

        Returns:
            The serialized commit data.
        """
        from ...utils.kvlm import kvlm_serialize
        return kvlm_serialize(self.kvlm)

    def deserialize(self, data: Any) -> None:
        """
        Populate the commit object from raw data.

        Args:
            data: Raw bytes or string representing the commit object.
        """
        from ...utils.kvlm import kvlm_parse
        self.kvlm: Dict[bytes, Any] = kvlm_parse(data)

    def init(self) -> None:
        """
        Initialize an empty commit object.
        """
        self.kvlm: Dict[bytes, Any] = {}
