def cmd_init(args):
    from ..core.repository import repo_create
    repo_create(args.path)
    print(f"Initialized empty sgit repository in {args.path}/.git/")