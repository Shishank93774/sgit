import os
import configparser
from typing import Optional


class GitRepository:
    """Represents a Git repository."""

    def __init__(self, path: str, force: bool = False) -> None:
        """
        Initialize a Git repository object.

        Args:
            path: Path to the repository worktree.
            force: If True, allow initialization even if repository is incomplete.
        Raises:
            Exception: If the path is not a valid Git repository.
        """
        self.worktree: str = path
        self.gitdir: str = os.path.join(path, ".git")
        self.conf: Optional[configparser.ConfigParser] = None

        if not (force or os.path.isdir(self.gitdir)):
            raise Exception(f"Not a Git repository {path}")

        # Lazy import to avoid circular dependency
        from ..utils.file_io import repo_file
        from ..utils.config import repo_default_config

        # Read configuration file in .git/config
        self.conf = configparser.ConfigParser()
        cf = repo_file(self, "config")

        if cf and os.path.exists(cf):
            self.conf.read([cf])
        elif not force:
            raise Exception("Configuration file missing")

        if not force:
            vers = int(self.conf.get("core", "repositoryformatversion"))
            if vers != 0:
                raise Exception(f"Unsupported repositoryformatversion {vers}")


def repo_create(path: str) -> GitRepository:
    """
    Create a new Git repository at the given path.

    Args:
        path: Path where the repository should be created.

    Returns:
        A GitRepository object representing the newly created repository.

    Raises:
        Exception: If the directory exists and is not empty, or if path is not a directory.
    """
    repo = GitRepository(path, True)

    if os.path.exists(repo.worktree):
        if not os.path.isdir(repo.worktree):
            raise Exception(f"{path} is not a directory!")
        if os.path.exists(repo.gitdir) and os.listdir(repo.gitdir):
            raise Exception(f"{path} is not empty!")
    else:
        os.makedirs(repo.worktree)

    # Lazy import
    from ..utils.file_io import repo_dir, repo_file
    from ..utils.config import repo_default_config

    # Create directories
    assert repo_dir(repo, "branches", mkdir=True)
    assert repo_dir(repo, "objects", mkdir=True)
    assert repo_dir(repo, "refs", "tags", mkdir=True)
    assert repo_dir(repo, "refs", "heads", mkdir=True)

    # .git/description
    with open(repo_file(repo, "description"), "w") as f:
        f.write(
            "Unnamed repository; edit this file 'description' to name the repository\n"
        )

    # .git/HEAD
    with open(repo_file(repo, "HEAD"), "w") as f:
        f.write("ref: refs/heads/master\n")

    # .git/config
    with open(repo_file(repo, "config"), "w") as f:
        config = repo_default_config()
        config.write(f)

    return repo
