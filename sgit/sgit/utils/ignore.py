import os
from fnmatch import fnmatch
from typing import List, Optional, Tuple


def gitignore_parse1(raw: str) -> Optional[Tuple[str, bool]]:
    """
    Parse a single line of a .gitignore file.

    Args:
        raw: Line from .gitignore file.

    Returns:
        Tuple of (pattern, True/False) or None if comment/empty line.
        True = include (ignore), False = negate pattern
    """
    raw = raw.strip()
    if not raw or raw.startswith("#"):
        return None
    elif raw.startswith("!"):
        return (raw[1:], False)
    elif raw.startswith("\\"):
        return (raw[1:], True)
    return (raw, True)


def gitignore_parse(lines: List[str]) -> List[Tuple[str, bool]]:
    """
    Parse multiple lines from a .gitignore file.

    Args:
        lines: List of strings.

    Returns:
        List of parsed (pattern, include_flag) tuples.
    """
    res = []
    for line in lines:
        parsed = gitignore_parse1(line)
        if parsed:
            res.append(parsed)
    return res


class GitIgnore:
    """Container for all Git ignore rules."""
    def __init__(self):
        self.absolute: List[List[Tuple[str, bool]]] = []
        self.scoped: dict[str, List[Tuple[str, bool]]] = {}


def gitignore_read(repo) -> GitIgnore:
    """
    Read ignore rules from repository.

    Includes:
        - .git/info/exclude
        - global XDG ignore file
        - index .gitignore files

    Args:
        repo: Repository object.

    Returns:
        GitIgnore object containing all rules.
    """
    res = GitIgnore()

    # Local config
    repo_file_path = os.path.join(repo.gitdir, "info/exclude")
    if os.path.exists(repo_file_path):
        with open(repo_file_path, "r") as f:
            res.absolute.append(gitignore_parse(f.readlines()))

    # Global config
    config_home = os.environ.get("XDG_CONFIG_HOME", "~/.config")
    global_file = os.path.join(os.path.expanduser(config_home), "git/ignore")
    if os.path.exists(global_file):
        with open(global_file, "r") as f:
            res.absolute.append(gitignore_parse(f.readlines()))

    # .gitignore in index
    from ..core.index import index_read
    from ..utils.hashing import object_read

    index = index_read(repo)
    for entry in index.entries:
        if entry.name.endswith(".gitignore"):
            dir_name = os.path.dirname(entry.name)
            contents = object_read(repo, entry.sha)
            lines = contents.blobdata.decode("utf-8").splitlines()
            res.scoped[dir_name] = gitignore_parse(lines)

    return res


def check_ignore1(rules: List[Tuple[str, bool]], path: str) -> Optional[bool]:
    """Check a path against a set of ignore rules."""
    for pattern, value in rules:
        if fnmatch(path, pattern):
            return value
    return None


def check_ignore_scoped(rules: dict[str, List[Tuple[str, bool]]], path: str) -> Optional[bool]:
    """Check scoped ignore rules from directory up to root."""
    parent = os.path.dirname(path)
    while parent:
        if parent in rules:
            result = check_ignore1(rules[parent], path)
            if result is not None:
                return result
        parent = os.path.dirname(parent)
        if parent == "":
            break
    return None


def check_ignore_absolute(rules: List[List[Tuple[str, bool]]], path: str) -> bool:
    """Check absolute/global ignore rules."""
    for ruleset in rules:
        result = check_ignore1(ruleset, path)
        if result is not None:
            return result
    return False


def check_ignore(rules: GitIgnore, path: str) -> bool:
    """
    Determine if a path should be ignored.

    Args:
        rules: GitIgnore rules container.
        path: Relative path from repo root.

    Returns:
        True if ignored, False otherwise.
    """
    if os.path.isabs(path):
        raise Exception("Path must be relative to repository root")

    result = check_ignore_scoped(rules.scoped, path)
    if result is not None:
        return result

    return check_ignore_absolute(rules.absolute, path)


def cmd_check_ignore(args):
    """Command-line utility to check which paths are ignored."""
    from .file_io import repo_find
    repo = repo_find()
    rules = gitignore_read(repo)

    for path in args.path:
        if check_ignore(rules, path):
            print(path)