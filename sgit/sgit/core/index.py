import os
from datetime import datetime
import pwd
import grp


class GitIndexEntry:
    def __init__(self, ctime=None, mtime=None, dev=None, ino=None, mode_type=None,
                 mode_perms=None, uid=None, gid=None, fsize=None, sha=None,
                 flag_assume_valid=None, flag_stage=None, name=None):
        self.ctime = ctime
        self.mtime = mtime
        self.dev = dev
        self.ino = ino
        self.mode_type = mode_type
        self.mode_perms = mode_perms
        self.uid = uid
        self.gid = gid
        self.fsize = fsize
        self.sha = sha
        self.flag_assume_valid = flag_assume_valid
        self.flag_stage = flag_stage
        self.name = name


class GitIndex:
    def __init__(self, version=2, entries=None):
        self.version = version
        self.entries = entries if entries is not None else []


def index_read(repo):
    from ..utils.file_io import repo_file
    index_file = repo_file(repo, "index")

    if not os.path.exists(index_file):
        return GitIndex()

    with open(index_file, 'rb') as f:
        raw = f.read()

    if len(raw) == 0:
        return GitIndex()

    if len(raw) < 12:
        return GitIndex()

    header = raw[0:12]
    sign = header[0:4]
    if sign != b"DIRC":
        return GitIndex()

    version = int.from_bytes(header[4:8], "big")
    if version != 2:
        return GitIndex()

    count = int.from_bytes(header[8:12], "big")
    if count == 0:
        return GitIndex(version=version, entries=[])

    entries = []
    content = raw[12:]
    idx = 0

    for i in range(count):
        if idx + 62 > len(content):
            return GitIndex()

        # Parse entry (simplified)
        ctime_s = int.from_bytes(content[idx:idx + 4], "big")
        ctime_ns = int.from_bytes(content[idx + 4:idx + 8], "big")
        mtime_s = int.from_bytes(content[idx + 8:idx + 12], "big")
        mtime_ns = int.from_bytes(content[idx + 12:idx + 16], "big")
        dev = int.from_bytes(content[idx + 16:idx + 20], "big")
        ino = int.from_bytes(content[idx + 20:idx + 24], "big")

        mode = int.from_bytes(content[idx + 26:idx + 28], "big")
        mode_type = mode >> 12
        mode_perms = mode & 0b0000000111111111

        uid = int.from_bytes(content[idx + 28:idx + 32], "big")
        gid = int.from_bytes(content[idx + 32:idx + 36], "big")
        fsize = int.from_bytes(content[idx + 36:idx + 40], "big")
        sha = format(int.from_bytes(content[idx + 40:idx + 60], "big"), "040x")

        flags = int.from_bytes(content[idx + 60:idx + 62], "big")
        flag_assume_valid = (flags & 0x8000) != 0
        flag_stage = flags & 0x3000
        name_length = flags & 0x0FFF

        idx += 62

        # Parse name
        if name_length < 0x0FFF:
            if idx + name_length > len(content):
                return GitIndex()
            name_bytes = content[idx:idx + name_length]
            idx += name_length
        else:
            null_idx = content.find(b'\x00', idx)
            if null_idx == -1:
                return GitIndex()
            name_bytes = content[idx:null_idx]
            idx = null_idx + 1

        name = name_bytes.decode("utf-8", errors="replace")

        # Padding
        if idx % 8 != 0:
            pad = 8 - (idx % 8)
            if idx + pad > len(content):
                return GitIndex()
            idx += pad

        entries.append(GitIndexEntry(
            ctime=(ctime_s, ctime_ns), mtime=(mtime_s, mtime_ns),
            dev=dev, ino=ino, mode_type=mode_type, mode_perms=mode_perms,
            uid=uid, gid=gid, fsize=fsize, sha=sha,
            flag_assume_valid=flag_assume_valid, flag_stage=flag_stage, name=name
        ))

    return GitIndex(version=version, entries=entries)


def index_write(repo, index):
    from ..utils.file_io import repo_file

    with open(repo_file(repo, "index"), "wb") as f:
        f.write(b"DIRC")
        f.write(index.version.to_bytes(4, "big"))
        f.write(len(index.entries).to_bytes(4, "big"))

        idx = 0
        for e in index.entries:
            f.write(e.ctime[0].to_bytes(4, "big"))
            f.write(e.ctime[1].to_bytes(4, "big"))
            f.write(e.mtime[0].to_bytes(4, "big"))
            f.write(e.mtime[1].to_bytes(4, "big"))
            f.write(e.dev.to_bytes(4, "big"))
            f.write(e.ino.to_bytes(4, "big"))

            mode = (e.mode_type << 12) | e.mode_perms
            f.write(mode.to_bytes(4, "big"))

            f.write(e.uid.to_bytes(4, "big"))
            f.write(e.gid.to_bytes(4, "big"))
            f.write(e.fsize.to_bytes(4, "big"))
            f.write(int(e.sha, 16).to_bytes(20, "big"))

            flag_assume_valid = 0x1 << 15 if e.flag_assume_valid else 0
            name_bytes = e.name.encode("utf8")
            bytes_len = len(name_bytes)
            name_length = 0xFFF if bytes_len >= 0xFFF else bytes_len

            f.write((flag_assume_valid | e.flag_stage | name_length).to_bytes(2, "big"))
            f.write(name_bytes)
            f.write((0).to_bytes(1, "big"))

            idx += 62 + len(name_bytes) + 1
            if idx % 8 != 0:
                pad = 8 - (idx % 8)
                f.write((0).to_bytes(pad, "big"))
                idx += pad


def cmd_ls_files(args):
    from ..utils.file_io import repo_find
    repo = repo_find()
    index = index_read(repo)

    if args.verbose:
        print(f"Index file format v{index.version}, containing {len(index.entries)} entries.")

    for e in index.entries:
        print(e.name)
        if args.verbose:
            entry_type = {0b1000: "regular file", 0b1010: "symlink", 0b1110: "git link"}[e.mode_type]
            print(f"  {entry_type} with perms: {e.mode_perms:o}")
            print(f"  on blob: {e.sha}")
            print(
                f"  created: {datetime.fromtimestamp(e.ctime[0])}.{e.ctime[1]}, modified: {datetime.fromtimestamp(e.mtime[0])}.{e.mtime[1]}")
            print(f"  device: {e.dev}, inode: {e.ino}")
            print(f"  user: {pwd.getpwuid(e.uid).pw_name} ({e.uid})  group: {grp.getgrgid(e.gid).gr_name} ({e.gid})")
            print(f"  flags: stage={e.flag_stage} assume_valid={e.flag_assume_valid}")


def cmd_ls_tree(args):
    from ..utils.file_io import repo_find
    from ..utils.hashing import object_find, object_read

    repo = repo_find()

    def ls_tree(repo, ref, recursive=None, prefix=""):
        sha = object_find(repo, ref, fmt=b'tree')
        obj = object_read(repo, sha)

        for item in obj.items:
            if len(item.mode) == 5:
                typ = item.mode[0:1]
            else:
                typ = item.mode[0:2]

            match typ:
                case b'04':
                    typ = "tree"
                case b'10':
                    typ = "blob"
                case b'12':
                    typ = "blob"
                case b'16':
                    typ = "commit"
                case _:
                    raise Exception(f"Unknown type {typ}")

            if not (recursive and typ == "tree"):
                path_str = item.path.decode('utf-8') if isinstance(item.path, bytes) else item.path
                print(
                    f"{'0' * (6 - len(item.mode)) + item.mode.decode('ascii')} {typ} {item.sha}\t{os.path.join(prefix, path_str)}")
            else:
                path_str = item.path.decode('utf-8') if isinstance(item.path, bytes) else item.path
                ls_tree(repo, item.sha, recursive, os.path.join(prefix, path_str))

    ls_tree(repo, args.tree, args.recursive)