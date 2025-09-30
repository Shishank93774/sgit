from .base import GitObject

class GitCommit(GitObject):
    fmt = b'commit'

    def serialize(self):
        from ...utils.kvlm import kvlm_serialize
        return kvlm_serialize(self.kvlm)

    def deserialize(self, data):
        from ...utils.kvlm import kvlm_parse
        self.kvlm = kvlm_parse(data)

    def init(self):
        self.kvlm = {}