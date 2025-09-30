from typing import Optional, Any


class GitObject:
    """Base class for Git objects (blob, commit, tree, tag)."""

    def __init__(self, data: Optional[Any] = None) -> None:
        """
        Initialize a Git object.

        Args:
            data: Optional raw data to deserialize into the object.
                  If None, the object is initialized empty.
        """
        if data is not None:
            self.deserialize(data)
        else:
            self.init()

    def serialize(self) -> bytes:
        """
        Serialize the object to raw bytes.

        Returns:
            The serialized object as bytes.

        Raises:
            Exception: If not implemented in a subclass.
        """
        raise Exception("Unimplemented!")

    def deserialize(self, data: Any) -> None:
        """
        Populate the object from raw data.

        Args:
            data: Raw bytes or string representing the object.

        Raises:
            Exception: If not implemented in a subclass.
        """
        raise Exception("Unimplemented!")

    def init(self) -> None:
        """
        Initialize an empty object.
        Can be overridden in subclasses to set default values.
        """
        pass
