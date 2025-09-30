from .commit import GitCommit

class GitTag(GitCommit):
    """Git object representing an annotated tag."""

    fmt: bytes = b'tag'
