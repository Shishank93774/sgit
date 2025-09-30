import os
from typing import Optional, List


def repo_path(repo, *path: str) -> str:
    """
    Compute a path under the repository's .git directory.

    Args:
        repo: Git repository object.
        *path: Path segments to join.

    Returns:
        Full path under the repo's gitdir.
    """
    return os.path.join(repo.gitdir, *path)


def repo_file(repo, *path: str, mkdir: bool = False) -> Optional[str]:
    """
    Return the path to a file under the repository's gitdir, optionally creating parent directories.

    Args:
        repo: Git repository object.
        *path: Path segments.
        mkdir: Whether to create the parent directories if they don't exist.

    Returns:
        Path to the file or None if parent directory does not exist and mkdir is False.
    """
    if repo_dir(repo, *path[:-1], mkdir=mkdir):
        return repo_path(repo, *path)
    return None


def repo_dir(repo, *path: str, mkdir: bool = False) -> Optional[str]:
    """
    Return a directory path under the repository's gitdir, optionally creating it.

    Args:
        repo: Git repository object.
        *path: Path segments.
        mkdir: Whether to create the directory if it does not exist.

    Returns:
        Path to the directory or None if it does not exist and mkdir is False.
    """
    path = repo_path(repo, *path)

    if os.path.exists(path):
        if os.path.isdir(path):
            return path
        else:
            raise Exception(f"Not a directory: {path}")

    if mkdir:
        os.makedirs(path)
        return path
    else:
        return None


def repo_find(path: str = ".", required: bool = True):
    """
    Locate a Git repository starting from a given path, searching upward.

    Args:
        path: Starting directory path.
        required: If True, raise an exception if no repository is found.

    Returns:
        GitRepository object if found, else None if required=False.
    """
    path = os.path.realpath(path)

    if os.path.isdir(os.path.join(path, ".git")):
        from ..core.repository import GitRepository
        return GitRepository(path)

    parent = os.path.realpath(os.path.join(path, ".."))

    if parent == path:
        if required:
            raise Exception("No git directory found.")
        else:
            return None

    return repo_find(parent, required)


def object_resolve(repo, name: str) -> Optional[List[str]]:
    """
    Resolve a short or full object name, or reference, to SHA(s).

    Args:
        repo: Git repository object.
        name: Object name or reference (HEAD, branch, tag, or SHA prefix).

    Returns:
        List of matching SHA strings, or None if no matches found.
    """
    import re

    if not name or not name.strip():
        return None

    candidates = []
    hash_re = re.compile(r"^[0-9A-Fa-f]{4,40}$")

    if name == "HEAD":
        head_ref = ref_resolve(repo, "HEAD")
        if head_ref:
            return [head_ref]
        return None

    # Match SHA prefix
    if hash_re.match(name):
        name = name.lower()
        prefix = name[:2]
        path = repo_dir(repo, "objects", prefix, mkdir=False)
        if path:
            rem = name[2:]
            for f in os.listdir(path):
                if f.startswith(rem):
                    candidates.append(prefix + f)

    # Check branches and tags
    for ref_prefix in ["refs/tags/", "refs/heads/"]:
        ref_path = repo_file(repo, ref_prefix + name)
        if ref_path and os.path.exists(ref_path):
            with open(ref_path, 'r') as f:
                sha = f.read().strip()
                if sha:
                    candidates.append(sha)

    return candidates if candidates else None


def ref_resolve(repo, ref: str) -> Optional[str]:
    """
    Resolve a Git reference to its SHA-1 hash.

    Args:
        repo: Git repository object.
        ref: Reference path (e.g., HEAD, refs/heads/master).

    Returns:
        SHA string if resolved, else None.
    """
    path = repo_file(repo, ref)
    if not path or not os.path.isfile(path):
        return None
    with open(path, "r") as f:
        data = f.read().strip()
    if data.startswith("ref: "):
        return ref_resolve(repo, data[5:])
    return data