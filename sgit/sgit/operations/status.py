import os
from typing import Dict


def cmd_status(args) -> None:
    """
    Display the status of the repository, including:
    - Current branch
    - Changes staged for commit
    - Changes not staged for commit
    - Untracked files

    Args:
        args: Command-line arguments (not used directly here).
    """
    from ..utils.file_io import repo_find
    from ..core.index import index_read
    from ..core.refs import branch_get_active, ref_resolve
    from ..utils.ignore import gitignore_read, check_ignore
    from ..utils.hashing import object_hash, object_read, object_find

    repo = repo_find()

    # Branch info
    branch = branch_get_active(repo)
    if branch:
        print(f"On branch {branch}")
    else:
        head_sha = ref_resolve(repo, "HEAD")
        if head_sha:
            print(f"HEAD detached at {head_sha[:7]}")
        else:
            print("On branch master (no commits yet)")

    index = index_read(repo)
    if index is None:
        index = type("EmptyIndex", (), {"entries": []})()

    print("\nChanges to be committed:")

    def tree_to_dict(repo, ref: str, prefix: str = "") -> Dict[str, str]:
        """
        Convert a tree object to a dict mapping file paths to SHA-1 hashes.

        Args:
            repo: Repository object.
            ref: Tree or commit reference.
            prefix: Path prefix for recursion.

        Returns:
            Dictionary of file paths -> SHA.
        """
        res = {}
        tree_sha = object_find(repo, ref, fmt=b'tree')
        if tree_sha is None:
            return res

        tree = object_read(repo, tree_sha)
        for leaf in tree.items:
            leaf_path = leaf.path.decode("utf-8") if isinstance(leaf.path, bytes) else leaf.path
            full_path = os.path.join(prefix, leaf_path)

            if leaf.mode.startswith(b'04'):  # Directory
                res.update(tree_to_dict(repo, leaf.sha, full_path))
            else:
                res[full_path] = leaf.sha
        return res

    head_tree = tree_to_dict(repo, "HEAD")

    # Compare index vs HEAD
    if not head_tree:
        for entry in index.entries:
            print(f"  new file: {entry.name}")
    else:
        for entry in index.entries:
            if entry.name in head_tree:
                if head_tree[entry.name] != entry.sha:
                    print(f"  modified: {entry.name}")
                del head_tree[entry.name]
            else:
                print(f"  new file: {entry.name}")

        for filename in head_tree:
            print(f"  deleted:  {filename}")

    # Changes not staged for commit
    print("\nChanges not staged for commit:")
    ignore = gitignore_read(repo)
    gitdir_prefix = repo.gitdir + os.sep
    all_files = []

    for root, dirs, files in os.walk(repo.worktree, topdown=True):
        if root == repo.gitdir or root.startswith(gitdir_prefix):
            continue
        for f in files:
            rel_path = os.path.relpath(os.path.join(root, f), repo.worktree)
            all_files.append(rel_path)

    for entry in index.entries:
        full_path = os.path.join(repo.worktree, entry.name)
        if not os.path.exists(full_path):
            print(f"  deleted:  {entry.name}")
        else:
            stat = os.stat(full_path)
            ctime_ns = entry.ctime[0] * 10**9 + entry.ctime[1]
            mtime_ns = entry.mtime[0] * 10**9 + entry.mtime[1]

            stat_ctime_ns = getattr(stat, 'st_ctime_ns', stat.st_ctime * 10**9)
            stat_mtime_ns = getattr(stat, 'st_mtime_ns', stat.st_mtime * 10**9)

            if stat_ctime_ns != ctime_ns or stat_mtime_ns != mtime_ns:
                with open(full_path, "rb") as f:
                    new_sha = object_hash(f, b"blob", None)
                    if new_sha != entry.sha:
                        print(f"  modified: {entry.name}")

        if entry.name in all_files:
            all_files.remove(entry.name)

    # Untracked files
    print("\nUntracked files:")
    for f in all_files:
        if not check_ignore(ignore, f):
            print(f"  {f}")
