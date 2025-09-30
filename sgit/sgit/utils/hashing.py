import os
import zlib
import hashlib
import re
import sys
from typing import Optional


def object_read(repo, sha: str):
    """
    Read a Git object by its SHA from the repository.

    Args:
        repo: Git repository object.
        sha: SHA string of the object.

    Returns:
        An instance of the appropriate Git object class (Commit, Tree, Blob, or Tag).

    Raises:
        Exception if the object is missing, corrupted, or of unknown type.
    """
    from .file_io import repo_file

    path = repo_file(repo, "objects", sha[:2], sha[2:], mkdir=False)

    if not os.path.exists(path):
        raise Exception(f"Object {sha} does not exist!")

    with open(path, "rb") as f:
        raw = zlib.decompress(f.read())

        x = raw.find(b' ')
        fmt = raw[:x]

        y = raw.find(b'\x00', x)
        size = int(raw[x:y].decode("ascii"))

        if size != len(raw) - (y + 1):
            raise Exception(f"Object {sha} is corrupt: bad length")

        # Lazy import of object classes
        if fmt == b'commit':
            from ..core.objects.commit import GitCommit
            cls = GitCommit
        elif fmt == b'tree':
            from ..core.objects.tree import GitTree
            cls = GitTree
        elif fmt == b'tag':
            from ..core.objects.tag import GitTag
            cls = GitTag
        elif fmt == b'blob':
            from ..core.objects.blob import GitBlob
            cls = GitBlob
        else:
            raise Exception(f"Unknown type {fmt.decode('ascii')} for object {sha}")

        return cls(raw[y + 1:])


def object_write(obj, repo=None) -> str:
    """
    Write a Git object to the repository.

    Args:
        obj: Git object instance.
        repo: Optional Git repository to store the object.

    Returns:
        SHA-1 hash of the object.
    """
    data = obj.serialize()
    result = obj.fmt + b' ' + str(len(data)).encode() + b'\x00' + data
    sha = hashlib.sha1(result).hexdigest()

    if repo:
        from .file_io import repo_file
        path = repo_file(repo, "objects", sha[:2], sha[2:], mkdir=True)
        if not os.path.exists(path):
            with open(path, "wb") as f:
                f.write(zlib.compress(result))
    return sha


def object_hash(fd, fmt: bytes, repo=None) -> str:
    """
    Hash the content of a file descriptor as a Git object and optionally store it.

    Args:
        fd: File descriptor (opened in binary mode).
        fmt: Git object type (b'blob', b'tree', b'commit', b'tag').
        repo: Optional Git repository to store the object.

    Returns:
        SHA-1 of the object.
    """
    data = fd.read()

    # Lazy import based on type
    if fmt == b'commit':
        from ..core.objects.commit import GitCommit
        obj = GitCommit(data)
    elif fmt == b'tree':
        from ..core.objects.tree import GitTree
        obj = GitTree(data)
    elif fmt == b'tag':
        from ..core.objects.tag import GitTag
        obj = GitTag(data)
    elif fmt == b'blob':
        from ..core.objects.blob import GitBlob
        obj = GitBlob(data)
    else:
        raise Exception(f"Unknown type {fmt}!")

    return object_write(obj, repo)


def object_find(repo, name: str, fmt: Optional[bytes] = None, follow: bool = True) -> Optional[str]:
    """
    Find an object by name (SHA or reference), optionally filtering by type.

    Args:
        repo: Git repository object.
        name: Reference name, SHA, or branch/tag.
        fmt: Optional object type to filter.
        follow: Whether to follow tags/commit-tree links.

    Returns:
        SHA string if found, else None.

    Raises:
        Exception if reference is ambiguous or not found.
    """
    from .file_io import object_resolve

    if not name:
        return None

    sha_list = object_resolve(repo, name)

    if not sha_list:
        if name == "HEAD" or re.match(r"^[0-9A-Fa-f]{4,40}$", name):
            return None
        raise Exception(f"No such reference {name} found.")

    if len(sha_list) > 1:
        raise Exception(f"Ambiguous reference {name}: {sha_list}")

    sha = sha_list[0]

    if not fmt:
        return sha

    while sha:
        obj = object_read(repo, sha)
        if obj.fmt == fmt:
            return sha

        if not follow:
            return None

        if obj.fmt == b'tag':
            sha = obj.kvlm[b'object'].decode('ascii')
        elif obj.fmt == b'commit' and fmt == b'tree':
            sha = obj.kvlm[b'tree'].decode('ascii')
        else:
            return None
    return None


def cmd_cat_file(args):
    """
    Implements `git cat-file` command to output object content.
    """
    from .file_io import repo_find
    repo = repo_find()

    try:
        obj_sha = object_find(repo, args.object, fmt=args.type.encode())
        if not obj_sha:
            print(f"Error: Object {args.object} not found", file=sys.stderr)
            sys.exit(1)

        obj = object_read(repo, obj_sha)
        data = obj.serialize()

        # Write to stdout
        if hasattr(sys.stdout, 'buffer'):
            sys.stdout.buffer.write(data)
        else:
            try:
                sys.stdout.write(data.decode('utf-8', errors='replace'))
            except (UnicodeDecodeError, AttributeError):
                sys.stdout.write(str(data))

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_hash_object(args):
    """
    Implements `git hash-object` command.
    """
    from .file_io import repo_find
    repo = repo_find() if args.write else None

    with open(args.path, "rb") as fd:
        sha = object_hash(fd, args.type.encode(), repo)
        print(sha)
