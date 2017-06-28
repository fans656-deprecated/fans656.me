# coding: utf-8
import itertools
from collections import defaultdict
from datetime import datetime

from f6 import each, bunch

import db
import utils
from errors import NotFound

def query_by_rels(rels, page=1, size=None):
    if not rels:
        preds = ['1']
    else:
        preds = ["l.rel = '{}' and n.data = '{}'".format(rel, data)
                 for rel, data in rels.items()]
    preds = ' and '.join(preds)

    # build link filter rules
    sql_where = '''
        where id in (
            select l.src from links as l inner join nodes as n
            on l.dst = n.id and {preds}
        ) order by ctime desc
    '''.format(preds=preds)

    # find total count
    sql = 'select count(id) from nodes ' + sql_where
    total = db.queryone('select count(id) from nodes ' + sql_where)
    size = size or total
    offset = (page - 1) * size
    if offset >= total:
        return bunch(nodes=[], page=page, size=size, total=total)

    # retrieve paged data
    r = db.query('select id, data, ctime from nodes '
                 + sql_where
                 + 'limit %s offset %s',
                 (size, offset))
    nodes = [Node(data, ctime=ctime, id=node_id)
             for node_id, data, ctime in r]
    assert nodes

    # retrieve links of nodes
    src_ids = ','.join('{}'.format(n.id) for n in nodes)
    r = db.query('select id, src, dst, rel from links '
                 + 'where src in ({})'.format(src_ids))
    links = [Link(link_id, src_id, dst_id, rel)
             for link_id, src_id, dst_id, rel in r]

    id_to_node = {n.id: n for n in nodes}

    dst_ids = ','.join('{}'.format(l.dst_id) for l in links)
    r = db.query('select id, data, ctime from nodes '
                 'where id in ({})'.format(dst_ids))
    new_nodes = [Node(data, ctime=ctime, id=node_id)
                 for node_id, data, ctime in r]
    id_to_node.update({n.id: n for n in new_nodes})

    node_id_to_links = defaultdict(lambda: [])
    for link in links:
        node_id_to_links[link.src_id].append(link)
        link.src = id_to_node[link.src_id]
        link.dst = id_to_node[link.dst_id]

    for node in nodes:
        node.links = node_id_to_links[node.id]

    return bunch(nodes=nodes, page=page, size=size, total=total)

def query_by_ids(node_ids, depth=1):
    node_ids = set(node_ids)
    visiting = set(node_ids)
    link_ids = set()
    for _ in xrange(depth):
        ids_str = ','.join(map(str, visiting))
        r = db.query('select id, src, dst from links '
                     'where src in ({ids})'.format(ids=ids_str))
        queried_ids = set()
        for link_id, src_id, dst_id in r:
            queried_ids.add(src_id)
            queried_ids.add(dst_id)
            link_ids.add(link_id)
        new_ids = queried_ids - visiting
        if len(new_ids) == 0:
            break
        node_ids |= new_ids;
        visiting = new_ids
    nodes = nodes_from_ids(node_ids)
    links = links_from_ids(link_ids)
    update_links_endpoints(nodes, links)
    return nodes

def query_by_id(node_id, depth=1):
    try:
        nodes = query_by_ids([node_id], depth)
        return next(n for n in nodes if n.id == node_id)
    except Exception as e:
        print utils.indented_exception(e)
        return None

class Node(object):

    def __init__(self, data, ctime=None, id=None, links=None):
        self.data = utils.to_unicode(data, 'Node().data')
        self.ctime = ctime or datetime.utcnow()
        self.id = id
        self.links = []

    @staticmethod
    def from_id(node_id):
        r = db.queryone('select data, ctime from nodes '
                        'where id = %s',
                        (node_id,))
        if not r:
            raise ValueError('no node with id={}'.format(node_id))
        data, ctime = r
        return Node(data.decode('utf8'),
                    ctime=ctime,
                    id=node_id,
                    links=links_from_src_id(node_id))

    @staticmethod
    def from_ref(ref):
        nodes = query_by_rels({'ref': ref}).nodes
        if not nodes:
            raise NotFound('no node with ref={}'.format(ref))
        elif len(nodes) == 1:
            return nodes[0]
        else:
            raise Response({
                'detail': 'multiple nodes with ref={} are found'.format(ref),
                'ids': [node.id for node in nodes]
            })

    @staticmethod
    def from_literal(literal):
        try:
            node = Node(literal['data'],
                        ctime=literal.get('ctime'),
                        )
            for link in literal.get('links', []):
                rel = link['rel']
                dst = link['dst']
                if isinstance(dst, int):
                    if dst == 0:
                        dst = node
                    else:
                        dst = Node.from_id(dst)
                elif isinstance(dst, (str, unicode)):
                    dst = Node.from_ref(dst)
                elif isinstance(dst, dict):
                    dst = Node.from_literal(dst)
                else:
                    raise Exception('unknown node literal type')
                node.link(rel, dst)
            return node
        except Exception as e:
            exc = utils.indented_exception(e)
            print exc
            raise ValueError('bad literal {}'.format(literal)
                             + '\n' + exc)

    def __eq__(self, o):
        return self.id == o.id

    def __hash__(self):
        return hash(self.id)

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

    def to_dict(self, depth=1):
        return node_to_dict(self, depth)

    def __repr__(self):
        return unicode(self).encode('utf8')

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
        nodes = set()
        q = [self]
        while q:
            node = q.pop()
            nodes.add(node)
            for link in self.links:
                nodes.add(link.dst)
        return list(nodes)

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
        return 'Node(id={}, data="{}"...)'.format(
            node.id, repr(node.data)[:20]
        )
        #return unicode(self).encode('utf8')

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

    def __init__(self, nodes, links, update_endpoints=True):
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

def node_to_dict(node, depth=1):
    if depth < 0:
        return node.id
    return {
        'id': node.id,
        'data': node.data,
        'ctime': node.ctime,
        'links': [{
            'id': link.id,
            'rel': link.rel,
            'dst': node_to_dict(link.dst, depth - 1)
        } for link in node.links]
    }

def links_from_src_id(node_id):
    return [
        Link(link_id, node_id, dst_id, rel=rel)
        for link_id, dst_id, rel
        in db.query('select id, dst, rel from links '
                    'where src = %s',
                    (node_id,))
    ]

def update_links_endpoints(nodes, links):
    id_to_node = {n.id: n for n in nodes}
    for link in links:
        src = id_to_node[link.src_id]
        dst = id_to_node[link.dst_id]
        link.src = src
        link.dst = dst
        src.links.append(link)

def incrementally_get_node(id_to_node, node_id):
    if node_id not in id_to_node:
        node = id_to_node[node_id] = Node.from_id(node_id)
        print 'added', node
        for link in node.links:
            link.src = incrementally_get_node(id_to_node, link.src_id)
            link.dst = incrementally_get_node(id_to_node, link.dst_id)
    return id_to_node[node_id]

def nodes_from_ids(ids):
    ids_str = ','.join(map(str, ids))
    r = db.query('select id, data, ctime from nodes '
                 'where id in ({})'.format(ids_str))
    return [Node(data, ctime=ctime, id=node_id)
            for node_id, data, ctime in r]

def links_from_ids(ids):
    ids_str = ','.join(map(str, ids))
    r = db.query('select id, src, dst, rel from links '
                 'where id in ({})'.format(ids_str))
    return [Link(id, src_id, dst_id, rel=rel)
            for id, src_id, dst_id, rel in r]

if __name__ == '__main__':
    from f6 import each
    from pprint import pprint

    #nodes = query_by_rels({'type': 'blog'}).nodes
    #nodes[4].graph.show()
    #print '-' * 70
    #node = query_by_id(1818)
    #node.graph.show()
    print Node.from_ref('blog')
