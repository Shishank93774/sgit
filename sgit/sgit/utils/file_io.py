import os


def repo_path(repo, *path):
    """Compute path under repo's gitdir."""
    return os.path.join(repo.gitdir, *path)


def repo_file(repo, *path, mkdir=False):
    """Same as repo_path, but create dirname(*path) if absent."""
    if repo_dir(repo, *path[:-1], mkdir=mkdir):
        return repo_path(repo, *path)


def repo_dir(repo, *path, mkdir=False):
    """Same as repo_path, but mkdir *path if absent if mkdir."""
    path = repo_path(repo, *path)

    if os.path.exists(path):
        if os.path.isdir(path):
            return path
        else:
            raise Exception(f"Not a directory {path}")

    if mkdir:
        os.makedirs(path)
        return path
    else:
        return None


def repo_find(path=".", required=True):
    """Find a Git repository starting from path."""
    path = os.path.realpath(path)

    if os.path.isdir(os.path.join(path, ".git")):
        # Import locally to avoid circular dependency
        from ..core.repository import GitRepository
        return GitRepository(path)

    parent = os.path.realpath(os.path.join(path, ".."))

    if parent == path:
        if required:
            raise Exception("No git directory.")
        else:
            return None

    return repo_find(parent, required)


def object_resolve(repo, name):
    """Resolve name to SHA."""
    import re
    from .file_io import repo_dir, repo_file

    if not name or not name.strip():
        return None

    candidates = []
    hash_re = re.compile(r"^[0-9A-Fa-f]{4,40}$")

    if name == "HEAD":
        head_ref = ref_resolve(repo, "HEAD")
        if head_ref:
            return [head_ref]
        else:
            return None

    if hash_re.match(name):
        name = name.lower()
        prefix = name[0:2]
        path = repo_dir(repo, "objects", prefix, mkdir=False)
        if path:
            rem = name[2:]
            for f in os.listdir(path):
                if f.startswith(rem):
                    candidates.append(prefix + f)

    for ref_prefix in ["refs/tags/", "refs/heads/"]:
        ref_path = repo_file(repo, ref_prefix + name)
        if os.path.exists(ref_path):
            with open(ref_path, 'r') as f:
                sha = f.read().strip()
                if sha:
                    candidates.append(sha)

    return candidates if candidates else None


def ref_resolve(repo, ref):
    """Resolve a reference to a SHA."""
    path = repo_file(repo, ref)
    if not path or not os.path.isfile(path):
        return None
    with open(path, "r") as f:
        data = f.read().strip()
    if data.startswith("ref: "):
        return ref_resolve(repo, data[5:])
    else:
        return data