import os
import re
from typing import Any, Dict, Optional, Union


def ref_resolve(repo: Any, ref: str) -> Optional[str]:
    """
    Resolve a Git reference to its final SHA-1 commit hash.

    Args:
        repo: The repository object.
        ref: The reference path (e.g., "HEAD", "refs/heads/master").

    Returns:
        The resolved SHA-1 hash as a string if found, otherwise None.
    """
    from ..utils.file_io import repo_file
    path = repo_file(repo, ref)
    if not path or not os.path.isfile(path):
        return None
    with open(path, "r") as f:
        data = f.read().strip()
    if data.startswith("ref: "):
        return ref_resolve(repo, data[5:])
    return data


def ref_list(repo: Any, path: Optional[str] = None) -> Dict[str, Union[str, dict]]:
    """
    Recursively list all references under the refs directory.

    Args:
        repo: The repository object.
        path: Optional starting path for refs. Defaults to repo/refs.

    Returns:
        A nested dictionary mapping reference names to their SHA-1 hashes
        or further dictionaries if subdirectories are present.
    """
    from ..utils.file_io import repo_dir
    if not path:
        path = repo_dir(repo, "refs")
    res: Dict[str, Union[str, dict]] = {}
    if not path or not os.path.isdir(path):
        return res
    for f in sorted(os.listdir(path)):
        can = os.path.join(path, f)
        if os.path.isdir(can):
            res[f] = ref_list(repo, can)
        else:
            res[f] = ref_resolve(repo, can)
    return res


def ref_create(repo: Any, ref_name: str, sha: str) -> None:
    """
    Create or update a reference to point to a given SHA-1 hash.

    Args:
        repo: The repository object.
        ref_name: The reference name (e.g., "heads/main").
        sha: The commit SHA-1 hash to associate with the ref.
    """
    from ..utils.file_io import repo_file
    with open(repo_file(repo, "refs/" + ref_name), "w") as fp:
        fp.write(sha + "\n")


def show_ref(repo: Any, refs: Dict[str, Union[str, dict]], with_hash: bool = True, prefix: str = "") -> None:
    """
    Print repository references in a tree-like format.

    Args:
        repo: The repository object.
        refs: A dictionary of references.
        with_hash: Whether to include SHA-1 hashes in the output.
        prefix: Optional prefix to prepend to reference names.
    """
    if prefix:
        prefix = prefix + "/"
    for k, v in refs.items():
        if isinstance(v, str) and with_hash:
            print(f"{v} {prefix}{k}")
        elif isinstance(v, str):
            print(f"{prefix}{k}")
        else:
            show_ref(repo, v, with_hash, f"{prefix}{k}")


def tag_create(repo: Any, name: str, ref: str, create_tag_object: bool = False) -> None:
    """
    Create a lightweight or annotated tag.

    Args:
        repo: The repository object.
        name: The name of the tag.
        ref: The reference (commit or object) to tag.
        create_tag_object: If True, creates an annotated tag object;
                           otherwise creates a lightweight tag.
    """
    from ..utils.hashing import object_find, object_write
    from ..core.objects.tag import GitTag

    sha = object_find(repo, ref)

    if create_tag_object:
        tag = GitTag()
        tag.kvlm = {}
        tag.kvlm[b'object'] = sha.encode()
        tag.kvlm[b'type'] = b'commit'
        tag.kvlm[b'tag'] = name.encode()
        tag.kvlm[b'tagger'] = b'Your Name <your.email@domain>'
        tag.kvlm[None] = b'Your tag message\n'

        tag_sha = object_write(tag, repo)
        ref_create(repo, "tags/" + name, tag_sha)
    else:
        ref_create(repo, "tags/" + name, sha)


def branch_get_active(repo: Any) -> Union[str, bool]:
    """
    Get the currently active branch name.

    Args:
        repo: The repository object.

    Returns:
        The branch name as a string if on a branch, otherwise False.
    """
    from ..utils.file_io import repo_file
    head_path = repo_file(repo, "HEAD")
    if not os.path.exists(head_path):
        return False
    with open(head_path, 'r') as f:
        head = f.read().strip()
    if head.startswith("ref: refs/heads/"):
        return head[16:]
    return False


def cmd_tag(args: Any) -> None:
    """
    CLI command for handling Git tags.

    Args:
        args: Parsed CLI arguments.
    """
    from ..utils.file_io import repo_find
    repo = repo_find()

    if args.name:
        tag_create(repo, args.name, args.object, args.create_tag_object)
    else:
        refs = ref_list(repo)
        show_ref(repo, refs.get("tags", {}), with_hash=False)


def cmd_rev_parse(args: Any) -> None:
    """
    CLI command to resolve a name to its SHA-1 object ID.

    Args:
        args: Parsed CLI arguments.
    """
    from ..utils.file_io import repo_find
    from ..utils.hashing import object_find

    repo = repo_find()
    fmt = args.type.encode() if args.type else None
    result = object_find(repo, args.name, fmt, follow=True)
    print(result if result else "")