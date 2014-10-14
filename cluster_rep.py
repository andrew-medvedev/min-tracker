__author__ = 'a.medvedev'


class ClusterRepresentation():
    def __init__(self, nodes, links):
        self.nodes = nodes
        self.links = links


class ClusterNode():
    def __init__(self, name, address, is_this):
        self.name = name
        self.address = address
        self.is_this = is_this


class ClusterLink():
    def __init__(self, a, b, on_port):
        self.a = a
        self.b = b
        self.on_port = on_port