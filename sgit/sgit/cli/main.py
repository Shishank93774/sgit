"""Main entry point for the sgit command-line interface."""

import sys
from argparse import Namespace
from typing import List
from .arg_parsers import build_arg_parser
from . import commands


def main(argv: List[str] | None = None) -> None:
    """
    Parse CLI arguments and dispatch to the appropriate command handler.

    Args:
        argv: Optional list of command-line arguments.
              If None, defaults to sys.argv[1:].

    Behavior:
        - Builds the argument parser with all supported commands.
        - Parses the provided arguments.
        - Looks up the corresponding command handler in the dispatch table.
        - Executes the handler or prints an error if the command is unknown.
    """
    if argv is None:
        argv = sys.argv[1:]

    parser = build_arg_parser()
    args: Namespace = parser.parse_args(argv)

    if not args.command:
        parser.print_help()
        return

    command_handlers = {
        "init": commands.cmd_init,
        "cat-file": commands.cmd_cat_file,
        "check-ignore": commands.cmd_check_ignore,
        "checkout": commands.cmd_checkout,
        "commit": commands.cmd_commit,
        "hash-object": commands.cmd_hash_object,
        "log": commands.cmd_log,
        "ls-files": commands.cmd_ls_files,
        "ls-tree": commands.cmd_ls_tree,
        "rev-parse": commands.cmd_rev_parse,
        "rm": commands.cmd_rm,
        "status": commands.cmd_status,
        "tag": commands.cmd_tag,
        "add": commands.cmd_add,
    }

    handler = command_handlers.get(args.command)
    if handler:
        handler(args)
    else:
        print(f"Unknown command: {args.command}")
        sys.exit(1)


if __name__ == "__main__":
    main()