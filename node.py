# coding: utf-8
import itertools
from datetime import datetime

from f6 import each

import db
from utils import NotFound

def query(*node_ids, **rels):
    def get_node(id_to_node, node_id):
        if node_id not in id_to_node:
            node = id_to_node[node_id] = Node(node_id)
            for link in node.links:
                link.src = get_node(id_to_node, link.src_id)
                link.dst = get_node(id_to_node, link.dst_id)
        return id_to_node[node_id]

    if not rels:
        preds = ['1']
    else:
        preds = ["l.rel = '{}' and n.data = '{}'".format(rel, data)
                 for rel, data in rels.items()]
    preds = ' and '.join(preds)
    sql = '''
        select id from nodes
        where id in (
            select l.src from links as l inner join nodes as n
            on l.dst = n.id and {preds}
        ) order by ctime desc
        '''.format(preds=preds)
    if node_ids:
        node_ids = set(node_ids) & set(db.query(sql))
    else:
        node_ids = db.query(sql)
    nodes = map(Node, node_ids)
    id_to_node = {n.id: n for n in nodes}
    for node in nodes:
        for link in node.links:
            link.src = get_node(id_to_node, link.src_id)
            link.dst = get_node(id_to_node, link.dst_id)
    return nodes

def get_node_by_id(node_id):
    try:
        return query(node_id)[0]
    except IndexError:
        raise

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

        link_datas = db.query(
            'select id, dst, rel from links where src = %s', (self.id,))
        self.links = [Link(link_id, self.id, dst_id, rel=rel)
                      for link_id, dst_id, rel in link_datas]

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
            ('links', [{
                'id': link.id,
                'rel': link.rel,
                'dst': link.dst.id,
                'detail': unicode(link),
            } for link in self.links]),
        ))

    def __unicode__(self):
        data = self.data
        if len(data) > 10:
            text = data[:7] + '...'
        else:
            text = data
        return u'Node(id={}, data={})'.format(self.id, text)

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
        print 'dumping node'
        print dict(self)
        if not self.id:
            with db.getdb() as c:
                db.execute('insert into nodes (data, ctime) values (%s,%s)',
                           (self.data.encode('utf8'), self.ctime), cursor=c)
                self.id = db.queryone('select last_insert_id() from nodes',
                                      cursor=c)
        else:
            # update data
            db.execute('update nodes set data = %s where id = %s',
                       (self.data.encode('utf8'), self.id))

            # delete links
            old_ids = db.query(
                'select id from links where src = %s', (self.id,))
            new_ids = each(self.links).id
            for link_id in set(old_ids) - set(new_ids):
                db.execute('delete from links where id = %s', link_id)

            # new links and updading links are handled by self.graph.dump
            # so this dump should not be used directly
            # I might write a independent Node lib in the future

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
        return unicode(self).encode('utf8')

    def __unicode__(self):
        if hasattr(self, 'src'):
            src = self.src
        else:
            src = 'Node(id={})'.format(self.src_id)
        if hasattr(self, 'dst'):
            dst = self.dst
        else:
            dst = 'Node(id={})'.format(self.dst_id)
        return u'Link(id={}, rel={}): {} ---> {}'.format(
            self.id, self.rel, src, dst)

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
        else:
            db.execute('update links set rel=%s, src=%s, dst=%s '
                       'where id = %s',
                       (self.rel, self.src.id, self.dst.id, self.id))

class Graph(object):

    def __init__(self, nodes, links):
        self.nodes = nodes
        self.links = links
        print
        print 'graph'
        self.show()
        print

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

def make_node_with_links_from_node_id(node_id):
    nodes = []
    node_ids = set([node_id])
    q = [Node(node_id)]
    while q:
        node = q.pop()
        nodes.append(node)
        for link in node.links:
            if link.dst_id not in node_ids:
                neighbor = Node(link.dst_id)
                node_ids.add(neighbor.id)
                q.append(neighbor)
    id_to_node = {node.id: node for node in nodes}
    for node in nodes:
        for link in node.links:
            link.src = id_to_node[link.src]
            link.dst = id_to_node[link.dst]
    return id_to_node[node_id]

if __name__ == '__main__':
    from f6 import each

    #query(type='blog')
    node = Node(u'好像可以了')
    s = unicode(node)
    print s
