import os
from datetime import datetime
from typing import Optional


def tree_from_index(repo: "GitRepository", index: "GitIndex") -> str:
    """
    Build a Git tree object from the repository index.

    Args:
        repo: The Git repository object.
        index: The Git index containing staged entries.

    Returns:
        SHA-1 hash of the root tree object.
    """
    contents = {"": []}

    for entry in index.entries:
        dirname = os.path.dirname(entry.name)
        key = dirname
        while key != "":
            if key not in contents:
                contents[key] = []
            key = os.path.dirname(key)
        contents[dirname].append(entry)

    sorted_paths = sorted(contents.keys(), key=len, reverse=True)
    sha = None

    for path in sorted_paths:
        from ..core.objects.tree import GitTree, GitTreeLeaf
        from ..utils.hashing import object_write
        from ..core.index import GitIndexEntry

        tree = GitTree()
        for item in contents[path]:
            if isinstance(item, GitIndexEntry):
                leaf_mode = f"{item.mode_type:02o}{item.mode_perms:04o}".encode("ascii")
                leaf = GitTreeLeaf(mode=leaf_mode, path=os.path.basename(item.name), sha=item.sha)
            else:
                leaf = GitTreeLeaf(mode=b"040000", path=item[0], sha=item[1])
            tree.items.append(leaf)

        sha = object_write(tree, repo)
        parent = os.path.dirname(path)
        base = os.path.basename(path)
        contents[parent].append((base, sha))

    return sha


def commit_create(
    repo: "GitRepository",
    tree: str,
    parent: Optional[str],
    author: str,
    timestamp: datetime,
    message: str
) -> str:
    """
    Create a commit object in the repository.

    Args:
        repo: The Git repository object.
        tree: SHA of the tree object representing the commit content.
        parent: SHA of the parent commit (if any).
        author: Author's name and email.
        timestamp: Commit timestamp.
        message: Commit message.

    Returns:
        SHA-1 hash of the created commit object.
    """
    from ..core.objects.commit import GitCommit
    from ..utils.hashing import object_write

    commit = GitCommit()
    commit.kvlm[b"tree"] = tree.encode("ascii")
    if parent:
        commit.kvlm[b"parent"] = parent.encode("ascii")

    message = message.strip() + "\n"
    offset = int(timestamp.astimezone().utcoffset().total_seconds())
    hours = offset // 3600
    minutes = (offset % 3600) // 60
    tz = "{}{:02}{:02}".format("+" if offset > 0 else "-", abs(hours), minutes)

    author_line = f"{author} {int(timestamp.timestamp())} {tz}"
    commit.kvlm[b"author"] = author_line.encode("utf8")
    commit.kvlm[b"committer"] = author_line.encode("utf8")
    commit.kvlm[None] = message.encode("utf8")

    return object_write(commit, repo)


def cmd_commit(args: "Namespace") -> None:
    """
    Handle 'commit' command: create a new commit from staged changes.

    Args:
        args: Command-line arguments with 'message' attribute.

    Prints:
        Information about the created commit and the branch/HEAD.
    """
    from ..utils.file_io import repo_find, repo_file
    from ..core.index import index_read
    from ..utils.config import gitconfig_read, gitconfig_user_get
    from ..utils.hashing import object_find
    from ..core.refs import branch_get_active
    from datetime import datetime

    if not args.message:
        print("Error: commit message required (-m)")
        return

    repo = repo_find()
    index = index_read(repo)
    tree = tree_from_index(repo, index)

    parent = object_find(repo, "HEAD")
    author = gitconfig_user_get(gitconfig_read())
    if not author:
        author = "Unknown User <unknown@example.com>"

    commit_sha = commit_create(repo, tree, parent, author, datetime.now(), args.message)

    active_branch = branch_get_active(repo)
    if active_branch:
        with open(repo_file(repo, "refs/heads", active_branch), "w") as fd:
            fd.write(commit_sha + "\n")
        print(f"[{active_branch} {commit_sha[:7]}] {args.message.strip()}")
    else:
        with open(repo_file(repo, "HEAD"), "w") as fd:
            fd.write(commit_sha + "\n")
        print(f"[detached HEAD {commit_sha[:7]}] {args.message.strip()}")
