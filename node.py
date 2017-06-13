# coding: utf-8
import hashlib
from datetime import datetime
from collections import deque

import db
from config import encoding

class Hashable(object):

    @property
    def hash_material(self):
        # child should override
        return ''

    @property
    def hash(self):
        if not hasattr(self, '_hash'):
            sha1 = hashlib.sha1()
            sha1.update(self.hash_material)
            self._hash = sha1.hexdigest()
        return self._hash

class Node(Hashable):

    def __init__(self, val, type):
        self.val = val
        self.type = type
        self.src_links = []
        self.dst_links = []
        self._id = None

    def link(self, node, type):
        link = Link(type, src=self, dst=node)
        self.dst_links.append(link)
        node.src_links.append(link)

    def __getitem__(self, attr):
        try:
            dsts = [l.dst for l in self.dst_links if l.val == attr]
            return dsts[0] if len(dsts) == 1 else dsts
        except IndexError:
            raise KeyError('{} has no link {}'.format(self, attr))

    def __repr__(self):
        return u'<Node {}: {}>'.format(self.type, self.val).encode(encoding)

    def __str__(self):
        return self.val

    @property
    def id(self):
        if not self._id:
            self._id = db.queryone('select id from nodes where hash = %s', (self.hash,))
        return self._id

    @property
    def hash_material(self):
        return self.type.encode(encoding) + self.val.encode(encoding)

    def persist(self, cursor):
        nodes = deque([self])
        while nodes:
            node = nodes.popleft()
            if is_persisted(node, cursor, 'nodes'):
                continue
            cursor.execute('insert into nodes (type, content, hash, ctime) values (%s,%s,%s,%s)',
                           (node.type.encode(encoding), node.val.encode(encoding),
                            node.hash, datetime.now()))
            for link in node.dst_links:
                link.persist(cursor)
                nodes.append(link.dst)

class Link(Hashable):

    def __init__(self, val, src, dst):
        self.val = val
        self.src = src
        self.dst = dst

    @property
    def hash_material(self):
        return self.val + self.src.hash + self.dst.hash

    def persist(self, cursor):
        if not is_persisted(self, cursor, 'links'):
            cursor.execute('insert into links (rel, src, dst, hash, ctime) values '
                           '(%s,%s,%s,%s,%s)',
                           (self.val.encode(encoding),
                            self.src.hash, self.dst.hash, self.hash, datetime.now()))

def is_persisted(obj, cursor, table):
    cursor.execute('select count(*) from {} where hash = %s'.format(table), (obj.hash,))
    persisted, = cursor.fetchone()
    return persisted

class Blog(Node):

    def __init__(self, content, title=None, tags=None):
        super(Blog, self).__init__(content, 'text.content')
        title = title or ''
        tags = tags or []
        self.link(Node(title, 'text.title'), type='title')
        for tag in tags:
            self.link(Node(tag, 'text.tag'), type='tag')

    @property
    def title(self):
        return unicode(self['title'])

    @property
    def content(self):
        return self.val

    @property
    def tags(self):
        return map(unicode, self['tag'])

    def __iter__(self):
        return iter([
            ('id', self.id),
            ('content', self.content),
            ('title', self.title),
            ('tags', self.tags),
        ])

if __name__ == '__main__':
    blog = Blog(u'这是内容', title=u'今天好吗', tags=['test', u'测试'])
    import db
    with db.getdb() as curosr:
        blog.persist(curosr)
