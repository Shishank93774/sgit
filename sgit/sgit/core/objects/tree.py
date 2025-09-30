from .base import GitObject

class GitTreeLeaf:
    def __init__(self, mode, path, sha):
        self.mode = mode
        self.path = path
        self.sha = sha

class GitTree(GitObject):
    fmt = b'tree'

    def serialize(self):
        from ...utils.tree_utils import tree_serialize
        return tree_serialize(self)

    def deserialize(self, data):
        from ...utils.tree_utils import tree_parse
        self.items = tree_parse(data)

    def init(self):
        self.items = []