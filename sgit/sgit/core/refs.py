import os
import re


def ref_resolve(repo, ref):
    from ..utils.file_io import repo_file
    path = repo_file(repo, ref)
    if not path or not os.path.isfile(path):
        return None
    with open(path, "r") as f:
        data = f.read().strip()
    if data.startswith("ref: "):
        return ref_resolve(repo, data[5:])
    else:
        return data


def ref_list(repo, path=None):
    from ..utils.file_io import repo_dir
    if not path:
        path = repo_dir(repo, "refs")
    res = {}
    if not path or not os.path.isdir(path):
        return res
    for f in sorted(os.listdir(path)):
        can = os.path.join(path, f)
        if os.path.isdir(can):
            res[f] = ref_list(repo, can)
        else:
            res[f] = ref_resolve(repo, can)
    return res


def ref_create(repo, ref_name, sha):
    from ..utils.file_io import repo_file
    with open(repo_file(repo, "refs/" + ref_name), "w") as fp:
        fp.write(sha + "\n")


def show_ref(repo, refs, with_hash=True, prefix=""):
    if prefix:
        prefix = prefix + "/"
    for k, v in refs.items():
        if isinstance(v, str) and with_hash:
            print(f"{v} {prefix}{k}")
        elif isinstance(v, str):
            print(f"{prefix}{k}")
        else:
            show_ref(repo, v, with_hash, f"{prefix}{k}")


def tag_create(repo, name, ref, create_tag_object=False):
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


def branch_get_active(repo):
    from ..utils.file_io import repo_file
    head_path = repo_file(repo, "HEAD")
    if not os.path.exists(head_path):
        return False
    with open(head_path, 'r') as f:
        head = f.read().strip()
    if head.startswith("ref: refs/heads/"):
        return head[16:]
    return False


def cmd_tag(args):
    from ..utils.file_io import repo_find
    repo = repo_find()

    if args.name:
        tag_create(repo, args.name, args.object, args.create_tag_object)
    else:
        refs = ref_list(repo)
        show_ref(repo, refs.get("tags", {}), with_hash=False)


def cmd_rev_parse(args):
    from ..utils.file_io import repo_find
    from ..utils.hashing import object_find

    repo = repo_find()
    fmt = args.type.encode() if args.type else None
    result = object_find(repo, args.name, fmt, follow=True)
    print(result if result else "")