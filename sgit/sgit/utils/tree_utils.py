from typing import List, Tuple, Union


class GitTreeLeaf:
    def __init__(self, mode: bytes, path: str, sha: str):
        """
        Represents a single entry in a Git tree (file or directory).

        Args:
            mode: File mode as bytes (e.g., b'100644' for a file).
            path: Path of the file or directory.
            sha: SHA-1 hash (hex string) of the object this leaf points to.
        """
        self.mode: bytes = mode
        self.path: str = path
        self.sha: str = sha


def tree_parse_single(raw: bytes, start: int) -> Tuple[int, GitTreeLeaf]:
    """
    Parse a single Git tree leaf from raw data starting at `start`.

    Args:
        raw: Raw tree bytes.
        start: Starting index.

    Returns:
        Tuple containing next position and GitTreeLeaf object.
    """
    x = raw.find(b' ', start)
    assert x - 5 == start or x - 6 == start, "Invalid tree entry"

    mode = raw[start:x]
    if len(mode) == 5:
        mode = b'0' + mode  # normalize mode length

    y = raw.find(b'\x00', x + 1)
    path_bytes = raw[x + 1:y]
    path = path_bytes.decode('utf-8')

    raw_sha = int.from_bytes(raw[y + 1:y + 21], 'big')
    sha = format(raw_sha, '040x')

    return y + 21, GitTreeLeaf(mode, path, sha)


def tree_parse(raw: bytes) -> List[GitTreeLeaf]:
    """
    Parse an entire Git tree object into leaves.

    Args:
        raw: Raw tree bytes.

    Returns:
        List of GitTreeLeaf objects.
    """
    pos = 0
    mx = len(raw)
    res: List[GitTreeLeaf] = []
    while pos < mx:
        pos, leaf = tree_parse_single(raw, pos)
        res.append(leaf)
    return res


def tree_leaf_sort_key(leaf: GitTreeLeaf) -> str:
    """
    Sorting key for GitTreeLeaf objects.

    Directories are sorted after files by appending a '/'.

    Args:
        leaf: GitTreeLeaf object.

    Returns:
        String used for sorting.
    """
    path_str = leaf.path.decode('utf-8') if isinstance(leaf.path, bytes) else leaf.path
    return path_str if leaf.mode.startswith(b"10") else path_str + "/"


def tree_serialize(obj) -> bytes:
    """
    Serialize a GitTree object into bytes.

    Args:
        obj: GitTree object with `items` attribute (list of GitTreeLeaf).

    Returns:
        Serialized tree bytes.
    """
    obj.items.sort(key=tree_leaf_sort_key)
    res = b''
    for leaf in obj.items:
        path_bytes = leaf.path.encode('utf-8') if isinstance(leaf.path, str) else leaf.path
        res += leaf.mode + b' ' + path_bytes + b'\x00'
        sha_bytes = int(leaf.sha, 16).to_bytes(20, 'big')
        res += sha_bytes
    return res
