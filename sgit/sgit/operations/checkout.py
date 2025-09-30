import os
from typing import Any


def tree_checkout(repo: "GitRepository", tree: Any, path: str) -> None:
    """
    Recursively checkout a Git tree object into a specified directory.

    Args:
        repo: The Git repository object.
        tree: A GitTree object to checkout.
        path: Destination path to checkout files.

    Raises:
        Exception: If an object type is unknown.
    """
    from ..utils.hashing import object_read, object_find

    for item in tree.items:
        obj = object_read(repo, object_find(repo, item.sha))
        dest = os.path.join(path, item.path)

        if obj.fmt == b'tree':
            os.makedirs(dest, exist_ok=True)
            tree_checkout(repo, obj, dest)
        elif obj.fmt == b'blob':
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            with open(dest, 'wb') as f:
                f.write(obj.blobdata)
        else:
            raise Exception(f"Unknown type {obj.fmt} for object {item.sha}")


def cmd_checkout(args: Any) -> None:
    """
    Command handler to checkout a commit into a directory.

    Args:
        args: Command-line arguments with 'commit' and 'path'.

    Raises:
        Exception: If target path is not a directory or not empty.
    """
    from ..utils.file_io import repo_find
    from ..utils.hashing import object_read, object_find

    repo = repo_find()
    commit_sha = object_find(repo, args.commit, fmt=b'commit')
    obj = object_read(repo, commit_sha)

    if obj.fmt == b'commit':
        tree_sha = obj.kvlm[b'tree'].decode('ascii')
        obj = object_read(repo, tree_sha)

    if os.path.exists(args.path):
        if not os.path.isdir(args.path):
            raise Exception(f"{args.path} is not a directory!")
        if os.listdir(args.path):
            raise Exception(f"{args.path} is not empty!")
    else:
        os.makedirs(args.path)

    tree_checkout(repo, obj, os.path.realpath(args.path))
    print(f"Checked out '{args.commit}' to '{args.path}'")