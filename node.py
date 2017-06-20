import itertools
from datetime import datetime

from f6 import each

import db
from utils import NotFound

def query(**options):
    if not options:
        preds = ['1']
    else:
        preds = ["l.rel = '{}' and n.data = '{}'".format(rel, data)
                 for rel, data in options.items()]
    preds = ' and '.join(preds)
    sql = '''
        select id from nodes
        where id in (
            select l.src from links as l inner join nodes as n
            on l.dst = n.id and {preds}
            order by n.ctime desc
        )
        '''.format(preds=preds)
    nodes = map(Node, db.query(sql))
    id_to_node = {n.id: n for n in nodes}
    for node in nodes:
        for link in node.links:
            link.src = get_node(id_to_node, link.src_id)
            link.dst = get_node(id_to_node, link.dst_id)
    return nodes

def get_node(id_to_node, node_id):
    if node_id not in id_to_node:
        node = id_to_node[node_id] = Node(node_id)
        for link in node.links:
            link.src = get_node(id_to_node, link.src_id)
            link.dst = get_node(id_to_node, link.dst_id)
    return id_to_node[node_id]

class Node(object):

    def __init__(self, id_or_data):
        if isinstance(id_or_data, int):
            node_id = id_or_data
            self.from_id(node_id)
        elif isinstance(id_or_data, (str, unicode)):
            data = id_or_data
            self.from_data(data)
        else:
            raise ValueError('non supported init method')

    def from_id(self, node_id):
        self.id = node_id

        r = db.queryone(
            'select data, ctime from nodes where id = %s', (self.id,))
        if not r:
            raise NotFound('node not found: id={}'.format(node_id))
        data, ctime = r
        self.data = data.decode('utf8')
        self.ctime = ctime

        self.links = [
            Link(link_id, self.id, dst_id, rel=rel) for link_id, dst_id, rel in
            db.query('select id, dst, rel from links where src = %s',
                     (self.id,))
        ]

    def from_data(self, data):
        self.id = None
        self.data = data
        self.links = []
        self.ctime = datetime.utcnow()

    def link(self, rel, dst_node):
        self.links.append(Link(rel, self, dst_node))

    def __iter__(self):
        return iter((
            ('id', self.id),
            ('data', self.data),
            ('ctime', self.ctime),
            ('links', map(str, self.links)),
        ))

    def __repr__(self):
        return 'Node(id={})'.format(self.id)

    def show(self):
        print '=' * 40, 'Node({})'.format(self.id)
        print 'content:'
        for line in self.data.split('\n'):
            print indent + line
        print 'links:'
        for link in self.links:
            print indent + '{}'.format(link)
        print

    def dump(self):
        if not self.id:
            with db.getdb() as c:
                db.execute('insert into nodes (data, ctime) values (%s,%s)',
                           (self.data.encode('utf8'), self.ctime), cursor=c)
                self.id = db.queryone('select last_insert_id() from nodes',
                                      cursor=c)
        else:
            pass  # TODO: update

    @property
    def graph(self):
        nodes = self.reachable_nodes
        links = set(itertools.chain(*each(nodes).links))
        return Graph(nodes, links)

    @property
    def reachable_nodes(self):
        nodes = []
        q = [self]
        while q:
            node = q.pop()
            nodes.append(node)
            q.extend(n for n in each(node.links).dst if n not in nodes)
        return nodes

class Link(object):

    def __init__(self, id_or_rel, *args, **kwargs):
        if isinstance(id_or_rel, int):
            link_id = id_or_rel
            self.from_id(link_id, *args, **kwargs)
        elif isinstance(id_or_rel, (str, unicode)):
            rel = id_or_rel
            self.from_data(rel, *args, **kwargs)
        else:
            raise ValueError('non supported init method')

    def from_id(self, link_id, src_id, dst_id, rel):
        self.id = link_id
        self.src_id = src_id
        self.dst_id = dst_id
        self.rel = rel.decode('utf-8')

    def from_data(self, rel, src_node, dst_node):
        self.id = None
        self.rel = rel
        self.src_id = None
        self.dst_id = None
        self.src = src_node
        self.dst = dst_node

    def __repr__(self):
        return 'Link({}, {}, {}, rel={})'.format(
            self.id, self.src_id, self.dst_id, repr(self.rel))

    def __str__(self):
        if self.id:
            return '{}: {} (id={})'.format(
                self.rel, self.dst.data[:10], self.id)
        else:
            return '{}: {}'.format(self.rel, self.dst.data[:10])

    def dump(self):
        if not self.id:
            with db.getdb() as c:
                db.execute('insert into links (rel, src, dst)'
                           'values (%s,%s,%s)',
                           (self.rel.encode('utf8'),
                            self.src.id,
                            self.dst.id), cursor=c)
                self.id = db.queryone('select last_insert_id() from links',
                                      cursor=c)

class Graph(object):

    def __init__(self, nodes, links):
        self.nodes = nodes
        self.links = links

    def dump(self):
        each(self.nodes).dump()
        each(self.links).dump()

    def show(self):
        print '=' * 20, 'nodes'
        for node in self.nodes:
            print node
        print '=' * 20, 'links'
        for link in self.links:
            print link
        print

if __name__ == '__main__':
    from f6 import each

    a = Node('foo')
    b = Node('bar')
    a.link('a', b)
    a.graph.dump()
    a.graph.show()
