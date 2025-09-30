from .base import GitObject
from typing import Any, List


class GitTreeLeaf:
    """Represents a single entry in a Git tree (file or subdirectory)."""

    def __init__(self, mode: str, path: str, sha: str) -> None:
        """
        Initialize a tree leaf.

        Args:
            mode: File mode (e.g., '100644' for a regular file).
            path: Path of the file or directory.
            sha: SHA-1 hash of the object this leaf points to.
        """
        self.mode: str = mode
        self.path: str = path
        self.sha: str = sha


class GitTree(GitObject):
    """Git object representing a tree (directory)."""

    fmt: bytes = b'tree'

    def serialize(self) -> bytes:
        """
        Serialize the tree object.

        Returns:
            Serialized tree object as bytes.
        """
        from ...utils.tree_utils import tree_serialize
        return tree_serialize(self)

    def deserialize(self, data: Any) -> None:
        """
        Populate the tree object from raw data.

        Args:
            data: Raw bytes representing the tree object.
        """
        from ...utils.tree_utils import tree_parse
        self.items: List[GitTreeLeaf] = tree_parse(data)

    def init(self) -> None:
        """Initialize an empty tree object."""
        self.items: List[GitTreeLeaf] = []
