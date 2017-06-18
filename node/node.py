# coding: utf-8
import hashlib
from datetime import datetime
from collections import deque

from utils import abstract
from config import codec

class Hashable(object):

    @property
    @abstract
    def hash_material(self):
        pass

    @property
    def hash(self):
        if not hasattr(self, '_hash'):
            sha1 = hashlib.sha1()
            sha1.update(self.hash_material)
            self._hash = sha1.hexdigest()
        return self._hash

    def __eq__(self, o):
        return self.hash == o.hash

    def __hash__(self):
        return hash(self.hash)

class Node(Hashable):

    def __init__(self, val_or_node, type=None):
        if isinstance(val_or_node, Node):
            node = val_or_node
            self.__dict__.update(node.__dict__)
        elif isinstance(val_or_node, (str, unicode)):
            val = val_or_node
            self.val = val
            self.type = type
            self.src_links = []
            self.dst_links = []
        else:
            raise ValueError('unsupported value of type {}'.format(type(val_or_node)))

    def link(self, node, type):
        link = Link(type, src=self, dst=node)
        self.dst_links.append(link)
        node.src_links.append(link)

    def from_node(self, node):
        assert isinstance(node, Node), 'must be of type Node'
        self.__dict__.update(node.__dict__)

    def __getitem__(self, attr):
        try:
            dsts = [l.dst for l in self.dst_links if l.val == attr]
            return dsts[0] if len(dsts) == 1 else dsts
        except IndexError:
            raise KeyError('{} has no link {}'.format(self, attr))

    def __repr__(self):
        return u'<Node {}: {}>'.format(self.type, self.val)

    def __str__(self):
        return self.val

    def __iter__(self):
        return iter((
            ('type', self.type),
            ('val', self.val),
            ('hash', self.hash),
        ))

    @property
    def reachable_nodes(self):
        nodes, _ = self.reachable_nodes_and_links
        return nodes

    @property
    def reachable_links(self):
        _, links = self.reachable_nodes_and_links
        return links

    @property
    def reachable_nodes_and_links(self):
        nodes = []
        links = []
        q = deque([self])
        while q:
            node = q.popleft()
            nodes.append(node)
            for link in node.dst_links:
                links.append(link)
                q.append(link.dst)
        return nodes, links

    @property
    def hash_material(self):
        return (self.type + self.val).encode(codec)

class Link(Hashable):

    def __init__(self, val, src, dst):
        self.val = val
        self.src = src
        self.dst = dst

    @property
    def hash_material(self):
        return self.val + self.src.hash + self.dst.hash

    def __iter__(self):
        return iter((
            ('val', self.val),
            ('src', self.src.hash),
            ('dst', self.dst.hash),
            ('hash', self.hash),
        ))

class Graph(object):

    def __init__(self, nodes, links):
        self.nodes = nodes
        self.links = links

    def __getitem__(self, pred):
        return [node for node in self.nodes if pred(node)]

    def __iter__(self):
        return iter((
            ('nodes', self.nodes),
            ('links', self.links),
        ))
