"""CLI command dispatchers with lazy imports to avoid circular dependencies.

Each function here wraps a corresponding implementation located in the
`operations`, `core`, or `utils` packages. The lazy imports ensure that
modules are only loaded when needed, reducing startup cost and preventing
circular import issues.
"""

from argparse import Namespace


def cmd_init(args: Namespace) -> None:
    """Initialize a new repository."""
    from ..operations.init import cmd_init as _cmd_init
    _cmd_init(args)


def cmd_cat_file(args: Namespace) -> None:
    """Display the content of a repository object."""
    from ..utils.hashing import cmd_cat_file as _cmd_cat_file
    _cmd_cat_file(args)


def cmd_check_ignore(args: Namespace) -> None:
    """Check path(s) against ignore rules."""
    from ..utils.ignore import cmd_check_ignore as _cmd_check_ignore
    _cmd_check_ignore(args)


def cmd_checkout(args: Namespace) -> None:
    """Checkout a commit inside a directory."""
    from ..operations.checkout import cmd_checkout as _cmd_checkout
    _cmd_checkout(args)


def cmd_commit(args: Namespace) -> None:
    """Record changes to the repository."""
    from ..operations.commit import cmd_commit as _cmd_commit
    _cmd_commit(args)


def cmd_hash_object(args: Namespace) -> None:
    """Compute object ID and optionally create a blob from a file."""
    from ..utils.hashing import cmd_hash_object as _cmd_hash_object
    _cmd_hash_object(args)


def cmd_log(args: Namespace) -> None:
    """Display the commit history."""
    from ..operations.log import cmd_log as _cmd_log
    _cmd_log(args)


def cmd_ls_files(args: Namespace) -> None:
    """List all staged files."""
    from ..core.index import cmd_ls_files as _cmd_ls_files
    _cmd_ls_files(args)


def cmd_ls_tree(args: Namespace) -> None:
    """Pretty-print a tree object."""
    from ..core.index import cmd_ls_tree as _cmd_ls_tree
    _cmd_ls_tree(args)


def cmd_rev_parse(args: Namespace) -> None:
    """Parse revision identifiers."""
    from ..core.refs import cmd_rev_parse as _cmd_rev_parse
    _cmd_rev_parse(args)


def cmd_rm(args: Namespace) -> None:
    """Remove files from the working tree and index."""
    from ..operations.add_remove import cmd_rm as _cmd_rm
    _cmd_rm(args)


def cmd_status(args: Namespace) -> None:
    """Show the working tree status."""
    from ..operations.status import cmd_status as _cmd_status
    _cmd_status(args)


def cmd_tag(args: Namespace) -> None:
    """List or create tags."""
    from ..core.refs import cmd_tag as _cmd_tag
    _cmd_tag(args)


def cmd_add(args: Namespace) -> None:
    """Add file contents to the index."""
    from ..operations.add_remove import cmd_add as _cmd_add
    _cmd_add(args)