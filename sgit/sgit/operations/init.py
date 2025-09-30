def cmd_init(args: "Namespace") -> None:
    """
    Initialize a new sgit repository at the specified path.

    Args:
        args: Command-line arguments containing the 'path' attribute.

    Prints:
        Confirmation message indicating the repository has been initialized.
    """
    from ..core.repository import repo_create

    repo_create(args.path)
    print(f"Initialized empty sgit repository in {args.path}/.git/")
