import itertools

from f6 import each

import db
from utils import NotFound

def query(options=None):
    options = options or {}
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
            self.load(node_id)
        elif isinstance(id_or_data, (str, unicode)):
            data = id_or_data
            self.data_init(data)
        else:
            raise ValueError('non supported init method')

    def load(self, node_id):
        self.id = node_id

        r = db.queryone(
            'select data, ctime from nodes where id = %s', (self.id,))
        if not r:
            raise NotFound()
        data, ctime = r
        self.data = data.decode('utf8')
        self.ctime = ctime

        self.links = [
            Link(link_id, self.id, dst_id, rel=rel) for link_id, dst_id, rel in
            db.query('select id, dst, rel from links where src = %s',
                     (self.id,))
        ]

    def data_init(self, data):
        self.id = None
        self.data = data
        self.links = []

    def __iter__(self):
        return iter((
            ('id', self.id),
            ('data', self.data),
            ('ctime', self.ctime),
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

class Link(object):

    def __init__(self, id_or_rel, *args, **kwargs):
        if isinstance(id_or_rel, int):
            link_id = id_or_rel
            self.load(link_id, *args, **kwargs)
        elif isinstance(id_or_rel, (str, unicode)):
            rel = id_or_rel
            self.data_init(rel, *args, **kwargs)
        else:
            raise ValueError('non supported init method')

    def load(self, link_id, src_id, dst_id, rel):
        self.id = link_id
        self.src_id = src_id
        self.dst_id = dst_id
        self.rel = rel.decode('utf-8')

    def __repr__(self):
        return 'Link({}, {}, {}, rel={})'.format(
            self.id, self.src_id, self.dst_id, repr(self.rel))

    def __str__(self):
        return '{}: {}'.format(self.rel, self.dst.data[:10])

node_from_id = Node
node_from_ref = lambda ref: query(ref=ref)[0]

if __name__ == '__main__':
    from f6 import each
    nodes = query(options={
        'ref': 'blog',
    })
    indent = ' ' * 4
    each(nodes).show()
    #nodes[0].links[0].dst.show()
