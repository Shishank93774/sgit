import os
from typing import List, Set, Tuple

def rm(repo: "GitRepository", paths: List[str], delete: bool = True, skip_missing: bool = False) -> None:
    """
    Remove files from the Git index and optionally from the working tree.

    Args:
        repo: The Git repository object.
        paths: List of file paths to remove.
        delete: If True, delete the files from the working directory as well.
        skip_missing: If True, skip files not present in the index.

    Raises:
        Exception: If paths are outside the worktree or not in the index.
    """
    from ..core.index import index_read, index_write, GitIndex

    index = index_read(repo) or GitIndex()
    worktree = repo.worktree + os.sep
    abspaths: Set[str] = set()

    for path in paths:
        abspath = os.path.abspath(path)
        if abspath.startswith(worktree):
            abspaths.add(abspath)
        else:
            raise Exception(f"Cannot remove paths outside of worktree: {path}")

    kept_entries = []
    remove = []

    for e in index.entries:
        full_path = os.path.join(repo.worktree, e.name)
        if full_path in abspaths:
            remove.append(full_path)
            abspaths.remove(full_path)
        else:
            kept_entries.append(e)

    if abspaths and not skip_missing:
        raise Exception(f"Cannot remove paths not in the index: {abspaths}")

    if delete:
        for path in remove:
            if os.path.exists(path):
                os.unlink(path)

    index.entries = kept_entries
    index_write(repo, index)


def add(repo: "GitRepository", paths: List[str]) -> None:
    """
    Add files to the Git index without modifying the working tree.

    Args:
        repo: The Git repository object.
        paths: List of file paths to add.

    Raises:
        Exception: If a path is not a file or is outside the repository.
    """
    rm(repo, paths, delete=False, skip_missing=True)
    worktree = repo.worktree + os.path.sep
    clean_paths: Set[Tuple[str, str]] = set()

    for path in paths:
        abspath = os.path.abspath(path)
        if not (abspath.startswith(worktree) and os.path.isfile(abspath)):
            raise Exception(f"Not a file, or outside the worktree: {path}")
        relpath = os.path.relpath(abspath, repo.worktree)
        clean_paths.add((abspath, relpath))

    from ..core.index import index_read, index_write, GitIndex, GitIndexEntry
    from ..utils.hashing import object_hash

    index = index_read(repo) or GitIndex()

    for abspath, relpath in clean_paths:
        with open(abspath, "rb") as fd:
            sha = object_hash(fd, b"blob", repo)
            stat = os.stat(abspath)

            ctime_s = int(stat.st_ctime)
            ctime_ns = stat.st_ctime_ns % 10 ** 9
            mtime_s = int(stat.st_mtime)
            mtime_ns = stat.st_mtime_ns % 10 ** 9

            entry = GitIndexEntry(
                ctime=(ctime_s, ctime_ns),
                mtime=(mtime_s, mtime_ns),
                dev=stat.st_dev,
                ino=stat.st_ino,
                mode_type=0b1000,
                mode_perms=0o644,
                uid=stat.st_uid,
                gid=stat.st_gid,
                fsize=stat.st_size,
                sha=sha,
                flag_assume_valid=False,
                flag_stage=0,
                name=relpath
            )
            index.entries.append(entry)

    index_write(repo, index)


def cmd_add(args) -> None:
    """
    Command handler to add files to the index.

    Args:
        args: Command-line arguments containing 'path'.
    """
    from ..utils.file_io import repo_find
    repo = repo_find()
    add(repo, args.path)


def cmd_rm(args) -> None:
    """
    Command handler to remove files from the index.

    Args:
        args: Command-line arguments containing 'path'.
    """
    from ..utils.file_io import repo_find
    repo = repo_find()
    rm(repo, args.path)
