import os
import zlib
import hashlib
import re
import sys


def object_read(repo, sha):
    from .file_io import repo_file

    path = repo_file(repo, "objects", sha[0:2], sha[2:], mkdir=False)

    if not os.path.exists(path):
        raise Exception(f"Object {sha} does not exist!")

    with open(path, "rb") as f:
        raw = zlib.decompress(f.read())

        x = raw.find(b' ')
        fmt = raw[0:x]

        y = raw.find(b'\x00', x)
        size = int(raw[x:y].decode("ascii"))

        if size != len(raw) - (y + 1):
            raise Exception(f"Object {sha} is corrupt: bad length")

        # Import object classes locally
        if fmt == b'commit':
            from ..core.objects.commit import GitCommit
            c = GitCommit
        elif fmt == b'tree':
            from ..core.objects.tree import GitTree
            c = GitTree
        elif fmt == b'tag':
            from ..core.objects.tag import GitTag
            c = GitTag
        elif fmt == b'blob':
            from ..core.objects.blob import GitBlob
            c = GitBlob
        else:
            raise Exception(f"Unknown type {fmt.decode('ascii')} for object {sha}")

        return c(raw[y + 1:])


def object_write(obj, repo=None):
    data = obj.serialize()
    result = obj.fmt + b' ' + str(len(data)).encode() + b'\x00' + data
    sha = hashlib.sha1(result).hexdigest()

    if repo:
        from .file_io import repo_file
        path = repo_file(repo, "objects", sha[0:2], sha[2:], mkdir=True)
        if not os.path.exists(path):
            with open(path, "wb") as f:
                f.write(zlib.compress(result))
    return sha


def object_hash(fd, fmt, repo=None):
    data = fd.read()

    # Import object classes locally
    if fmt == b'commit':
        from ..core.objects.commit import GitCommit
        obj = GitCommit(data)
    elif fmt == b'tree':
        from ..core.objects.tree import GitTree
        obj = GitTree(data)
    elif fmt == b'tag':
        from ..core.objects.tag import GitTag
        obj = GitTag(data)
    elif fmt == b'blob':
        from ..core.objects.blob import GitBlob
        obj = GitBlob(data)
    else:
        raise Exception(f"Unknown type {fmt}!")

    return object_write(obj, repo)


def object_find(repo, name, fmt=None, follow=True):
    from .file_io import object_resolve

    if not name:
        return None

    sha = object_resolve(repo, name)

    if not sha:
        if name == "HEAD":
            return None
        if re.match(r"^[0-9A-Fa-f]{4,40}$", name):
            return None
        raise Exception(f"No such reference {name} found.")

    if len(sha) > 1:
        raise Exception(f"Ambiguous reference {name}: {sha}")

    sha = sha[0]

    if not fmt:
        return sha

    while True:
        if sha is None:
            return None

        obj = object_read(repo, sha)
        if obj.fmt == fmt:
            return sha

        if not follow:
            return None

        if obj.fmt == b'tag':
            sha = obj.kvlm[b'object'].decode('ascii')
        elif obj.fmt == b'commit' and fmt == b'tree':
            sha = obj.kvlm[b'tree'].decode('ascii')
        else:
            return None


def cmd_cat_file(args):
    from .file_io import repo_find
    repo = repo_find()

    try:
        obj_sha = object_find(repo, args.object, fmt=args.type.encode())
        if not obj_sha:
            print(f"Error: Object {args.object} not found", file=sys.stderr)
            sys.exit(1)

        obj = object_read(repo, obj_sha)
        data = obj.serialize()

        # Write to stdout - handle both text and binary safely
        if hasattr(sys.stdout, 'buffer'):
            # Normal execution - write binary
            sys.stdout.buffer.write(data)
        else:
            # Test environment - write as text or handle differently
            try:
                # Try to decode as text for testing
                sys.stdout.write(data.decode('utf-8', errors='replace'))
            except (UnicodeDecodeError, AttributeError):
                # If it's binary data, just write bytes directly
                sys.stdout.write(str(data))

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_hash_object(args):
    from .file_io import repo_find
    if args.write:
        repo = repo_find()
    else:
        repo = None

    with open(args.path, "rb") as fd:
        sha = object_hash(fd, args.type.encode(), repo)
        print(sha)