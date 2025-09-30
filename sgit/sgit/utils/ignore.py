import os
from fnmatch import fnmatch


def gitignore_parse1(raw):
    raw = raw.strip()
    if not raw or raw[0] == '#':
        return None
    elif raw[0] == '!':
        return (raw[1:], False)
    elif raw[0] == '\\':
        return (raw[1:], True)
    return (raw, True)


def gitignore_parse(lines):
    res = []
    for line in lines:
        parsed = gitignore_parse1(line)
        if parsed:
            res.append(parsed)
    return res


class GitIgnore:
    def __init__(self):
        self.absolute = []
        self.scoped = {}


def gitignore_read(repo):
    res = GitIgnore()

    # Read local config in .git/info/exclude
    repo_file_path = os.path.join(repo.gitdir, "info/exclude")
    if os.path.exists(repo_file_path):
        with open(repo_file_path, "r") as f:
            res.absolute.append(gitignore_parse(f.readlines()))

    # Global configuration
    config_home = os.environ.get("XDG_CONFIG_HOME", "~/.config")
    global_file = os.path.join(os.path.expanduser(config_home), "git/ignore")
    if os.path.exists(global_file):
        with open(global_file, "r") as f:
            res.absolute.append(gitignore_parse(f.readlines()))

    # .gitignore files in the index
    from ..core.index import index_read
    from ..utils.hashing import object_read

    index = index_read(repo)
    for entry in index.entries:
        if entry.name == ".gitignore" or entry.name.endswith("/.gitignore"):
            dir_name = os.path.dirname(entry.name)
            contents = object_read(repo, entry.sha)
            lines = contents.blobdata.decode("utf8").splitlines()
            res.scoped[dir_name] = gitignore_parse(lines)

    return res


def check_ignore1(rules, path):
    for pattern, value in rules:
        if fnmatch(path, pattern):
            return value
    return None


def check_ignore_scoped(rules, path):
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


def check_ignore_absolute(rules, path):
    for ruleset in rules:
        result = check_ignore1(ruleset, path)
        if result is not None:
            return result
    return False


def check_ignore(rules, path):
    if os.path.isabs(path):
        raise Exception("Path must be relative to repository root")

    result = check_ignore_scoped(rules.scoped, path)
    if result is not None:
        return result

    return check_ignore_absolute(rules.absolute, path)


def cmd_check_ignore(args):
    from .file_io import repo_find
    repo = repo_find()
    rules = gitignore_read(repo)

    for path in args.path:
        if check_ignore(rules, path):
            print(path)