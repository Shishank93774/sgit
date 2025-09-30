from typing import Set, Union


def log_graphviz(repo: "GitRepository", sha: str, seen: Set[str]) -> None:
    """
    Recursively print commit history in Graphviz DOT format.

    Args:
        repo: The repository object.
        sha: SHA-1 of the commit to log.
        seen: Set of already processed commit SHAs to avoid cycles.
    """
    if sha is None or sha in seen:
        return
    seen.add(sha)

    try:
        from ..utils.hashing import object_read
        commit = object_read(repo, sha)
    except Exception as e:
        print(f"  // Error reading commit {sha}: {e}")
        return

    if None in commit.kvlm:
        message = commit.kvlm[None].decode("utf-8", errors="replace").strip()
        message = message.replace('\\', '\\\\').replace('"', '\\"')
        if '\n' in message:
            message = message[:message.index('\n')]
    else:
        message = "No message"

    short_sha = sha[:7] if sha else "unknown"
    print(f'  "c_{sha}" [label="{short_sha}: {message}"]')

    if commit.fmt != b'commit':
        print(f"  // Object {sha} is not a commit")
        return

    if b'parent' not in commit.kvlm:
        return

    parents = commit.kvlm[b'parent']
    if not isinstance(parents, list):
        parents = [parents]

    for p in parents:
        p_str: str = p.decode("ascii") if isinstance(p, bytes) else str(p)
        print(f'  "c_{sha}" -> "c_{p_str}"')
        log_graphviz(repo, p_str, seen)


def cmd_log(args: "Namespace") -> None:
    """
    Display the commit history of the repository in Graphviz DOT format.

    Args:
        args: Command-line arguments containing the 'commit' attribute.
    """
    from ..utils.file_io import repo_find
    from ..utils.hashing import object_find

    repo = repo_find()
    commit_sha = object_find(repo, args.commit)

    if commit_sha is None:
        print("No commits yet in this repository")
        return

    print("digraph sgitlog {")
    print("  node [shape=rect]")
    log_graphviz(repo, commit_sha, set())
    print("}")
