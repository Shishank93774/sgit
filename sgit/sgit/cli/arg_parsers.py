"""Argument parser definitions for sgit CLI."""

import argparse
from argparse import ArgumentParser


def build_arg_parser() -> ArgumentParser:
    """
    Build and return the top-level argument parser for sgit.

    This parser defines all supported subcommands (init, cat-file, hash-object,
    log, ls-tree, checkout, tag, rev-parse, ls-files, check-ignore, status,
    rm, add, commit).
    """
    argparser = argparse.ArgumentParser(description="Write yourself a git!")
    argsubparsers = argparser.add_subparsers(title="Commands", dest="command")
    argsubparsers.required = True

    # Init command
    argsp = argsubparsers.add_parser(
        "init", help="Initialize a new, empty repository."
    )
    argsp.add_argument(
        "path",
        metavar="directory",
        nargs="?",
        default=".",
        help="Where to create the repository.",
    )

    # cat-file command
    argsp = argsubparsers.add_parser(
        "cat-file", help="Provide content of repository objects"
    )
    argsp.add_argument(
        "type", choices=["blob", "commit", "tag", "tree"], help="Specify the type"
    )
    argsp.add_argument("object", help="The object to display")

    # hash-object command
    argsp = argsubparsers.add_parser(
        "hash-object",
        help="Compute object ID and optionally create a blob from a file",
    )
    argsp.add_argument(
        "-t",
        dest="type",
        choices=["blob", "commit", "tag", "tree"],
        default="blob",
        help="Specify the type",
    )
    argsp.add_argument(
        "-w",
        dest="write",
        action="store_true",
        help="Actually write the object into the database",
    )
    argsp.add_argument("path", help="Read object from <file>")

    # log command
    argsp = argsubparsers.add_parser("log", help="Display history of a given commit.")
    argsp.add_argument(
        "commit", default="HEAD", nargs="?", help="Commit to start at."
    )

    # ls-tree command
    argsp = argsubparsers.add_parser("ls-tree", help="Pretty-print a tree object.")
    argsp.add_argument(
        "-r",
        dest="recursive",
        action="store_true",
        help="Recursively list the objects in each tree.",
    )
    argsp.add_argument("tree", help="The tree-ish object to list.")

    # checkout command
    argsp = argsubparsers.add_parser(
        "checkout", help="Checkout a commit inside a directory."
    )
    argsp.add_argument("commit", help="The commit to checkout.")
    argsp.add_argument("path", help="An EMPTY directory to checkout into.")

    # tag command
    argsp = argsubparsers.add_parser("tag", help="List or create tags")
    argsp.add_argument(
        "-a",
        action="store_true",
        dest="create_tag_object",
        help="Create an annotated tag.",
    )
    argsp.add_argument("name", nargs="?", help="The new tag's name.")
    argsp.add_argument("object", default="HEAD", nargs="?", help="The object to tag.")

    # rev-parse command
    argsp = argsubparsers.add_parser("rev-parse", help="Parse revision identifiers.")
    argsp.add_argument(
        "--sgit-type",
        dest="type",
        choices=["blob", "commit", "tag", "tree"],
        default=None,
        help="Specify the expected type",
    )
    argsp.add_argument("name", help="The name to resolve.")

    # ls-files command
    argsp = argsubparsers.add_parser("ls-files", help="List all the staged files")
    argsp.add_argument(
        "--verbose", action="store_true", help="Show everything."
    )

    # check-ignore command
    argsp = argsubparsers.add_parser(
        "check-ignore", help="Check path(s) against ignore rules."
    )
    argsp.add_argument("path", nargs="+", help="Paths to check")

    # status command
    argsubparsers.add_parser("status", help="Show the working tree status.")

    # rm command
    argsp = argsubparsers.add_parser(
        "rm", help="Remove files from the working tree and the index."
    )
    argsp.add_argument("path", nargs="+", help="Files to remove")

    # add command
    argsp = argsubparsers.add_parser("add", help="Add file contents to the index.")
    argsp.add_argument("path", nargs="+", help="Files to add")

    # commit command
    argsp = argsubparsers.add_parser(
        "commit", help="Record changes to the repository."
    )
    argsp.add_argument(
        "-m",
        metavar="message",
        dest="message",
        help="Message to associate with this commit.",
    )

    return argparser