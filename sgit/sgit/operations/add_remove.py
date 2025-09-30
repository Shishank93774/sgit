import os


def rm(repo, paths, delete=True, skip_missing=False):
    from ..core.index import index_read, index_write, GitIndex

    index = index_read(repo)
    if index is None:
        index = GitIndex()

    worktree = repo.worktree + os.sep
    abspaths = set()

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

    if len(abspaths) > 0 and not skip_missing:
        raise Exception(f"Cannot remove paths not in the index: {abspaths}")

    if delete:
        for path in remove:
            if os.path.exists(path):
                os.unlink(path)

    index.entries = kept_entries
    index_write(repo, index)


def add(repo, paths):
    rm(repo, paths, delete=False, skip_missing=True)

    worktree = repo.worktree + os.path.sep
    clean_paths = set()

    for path in paths:
        abspath = os.path.abspath(path)
        if not (abspath.startswith(worktree) and os.path.isfile(abspath)):
            raise Exception(f"Not a file, or outside the worktree: {path}")
        relpath = os.path.relpath(abspath, repo.worktree)
        clean_paths.add((abspath, relpath))

    from ..core.index import index_read, index_write, GitIndexEntry
    from ..utils.hashing import object_hash

    index = index_read(repo)
    if index is None:
        index = GitIndex()

    for (abspath, relpath) in clean_paths:
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


def cmd_add(args):
    from ..utils.file_io import repo_find
    repo = repo_find()
    add(repo, args.path)


def cmd_rm(args):
    from ..utils.file_io import repo_find
    repo = repo_find()
    rm(repo, args.path)