class GitTreeLeaf:
    def __init__(self, mode, path, sha):
        self.mode = mode
        self.path = path
        self.sha = sha

def tree_parse_single(raw, start):
    x = raw.find(b' ', start)
    assert x - 5 == start or x - 6 == start

    mode = raw[start:x]
    if len(mode) == 5:
        mode = b'0' + mode

    y = raw.find(b'\x00', x + 1)
    path_bytes = raw[x + 1:y]
    path = path_bytes.decode('utf-8')

    raw_sha = int.from_bytes(raw[y + 1:y + 21], 'big')
    sha = format(raw_sha, '040x')

    return y + 21, GitTreeLeaf(mode, path, sha)

def tree_parse(raw):
    pos = 0
    mx = len(raw)
    res = []
    while pos < mx:
        pos, data = tree_parse_single(raw, pos)
        res.append(data)
    return res

def tree_leaf_sort_key(leaf):
    if isinstance(leaf.path, bytes):
        path_str = leaf.path.decode('utf-8')
    else:
        path_str = leaf.path

    if leaf.mode.startswith(b"10"):
        return path_str
    else:
        return path_str + "/"

def tree_serialize(obj):
    obj.items.sort(key=tree_leaf_sort_key)
    res = b''
    for i in obj.items:
        if isinstance(i.path, str):
            path_bytes = i.path.encode('utf-8')
        else:
            path_bytes = i.path
        res += i.mode + b' ' + path_bytes + b'\x00'
        sha = int(i.sha, 16)
        res += sha.to_bytes(20, 'big')
    return res