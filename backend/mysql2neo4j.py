import json
from datetime import datetime
from pprint import pprint

import requests
from f6 import bunch

import conf
from db import cypher

if conf.db_engine == 'mysql':
    import pymysql as DB
    conn_params = {
        'host': 'localhost',
        'user': conf.db_username,
        'passwd': conf.db_password,
        'db': conf.db_name,
    }
else:
    try:
        from pysqlite2 import dbapi2 as DB
    except ImportError:
        import sqlite3 as DB
    conn_params = {
        'database': 'all.db',
    }
from flask import g

def getdb():
    try:
        if not hasattr(g, 'db'):
            g.db = connect_db()
        return g.db
    except Exception:
        return connect_db()

def connect_db():
    return DB.connect(**conn_params)

def execute(*sql, **kwargs):
    cursor = kwargs.get('cursor')
    if cursor:
        c = cursor
        c.execute(*sql)
    else:
        with getdb() as c:
            c.execute(*sql)

def query(*sql, **kwargs):
    cursor = kwargs.get('cursor')
    if cursor:
        c = cursor
        c.execute(*sql)
        r = c.fetchall()
    else:
        with getdb() as c:
            c.execute(*sql)
            r = c.fetchall()
    if r and len(r[0]) == 1:
        r = [t[0] for t in r]
    return r

def queryone(*sql, **kwargs):
    r = query(*sql, **kwargs)
    return r[0] if r else None

def init_db(purge=False, quite=False):
    backup_db()

    print '*** initing database ***'

    outter_purge = purge

    def create_table(name, columns, purge=None):
        if purge is None:
            purge = outter_purge
        if purge:
            c.execute('drop table if exists {}'.format(name))
        c.execute('create table if not exists {} ({})'.format(name, columns))

    db = getdb()
    c = db.cursor()

    create_table('users', (
        'username varchar(255) unique,'
        'salt char(64),'
        'hashed_pwd char(64),'
        'iterations int'
    ))
    create_table('sessions', (
        'id char(64) unique,'
        'username varchar(255),'
        'ctime datetime,'
        'expires datetime'
    ))
    create_table('nodes', (
        'id serial,'
        'data longtext,'
        'ctime datetime default current_timestamp,'
        'mtime datetime default current_timestamp on update current_timestamp'
    ), purge=True)
    create_table('links', (
        'id serial,'
        'rel longtext,'
        'src bigint unsigned,'
        'dst bigint unsigned,'
        'ctime datetime default current_timestamp,'
        'mtime datetime default current_timestamp on update current_timestamp'
    ), purge=True)
    if not quite:
        print 'database inited'

def managedb():
    import os
    os.system('mysql -u{} -p{} -D{}'.format(
        conf.db_username,
        conf.db_password,
        conf.db_name,
    ))

def insert_meta_nodes():
    from node import Node
    blog = Node('blog')
    blog.link('ref', blog)
    blog.graph.dump()

def backup_db():
    fname = '{}-mysqldump-{}.sql'.format(
        datetime.now().strftime('%Y%m%d%H%M%S'),
        conf.db_name,
    )
    print '*** Backuping database {} to {} ***'.format(
        conf.db_name,
        fname,
    )
    os.system('mysqldump -u{} -p{} {} > {}'.format(
        conf.db_username,
        conf.db_password,
        conf.db_name,
        fname,
    ))

blogs_query = '''
select id, data, ctime from nodes
where id in (
    select l.src from links as l inner join nodes as n
    on l.dst = n.id
    where l.rel = 'type' and n.data = 'blog'
) order by ctime
'''

tags_query = '''
select l.src, n.data from links as l inner join nodes as n
on l.dst = n.id
where l.rel = 'tag'
'''

titles_query = '''
select l.src, n.data from links as l inner join nodes as n
on l.dst = n.id
where l.rel = 'title'
'''

sources_query = '''
select l.src, n.data from links as l inner join nodes as n
on l.dst = n.id
where l.rel = 'source'
'''


def make_blogs():
    blogs = {}
    for blog_id, data, ctime in query(blogs_query):
        blogs[blog_id] = bunch(
            data=data.decode('utf8'),
            ctime=str(ctime) + ' UTC',
            tags=[],
            title='',
            source='',
        )

    # add title
    for blog_id, title in query(titles_query):
        blogs[blog_id].title = title.decode('utf8')

    # add source
    for blog_id, source in query(sources_query):
        blogs[blog_id].source = source.decode('utf8')

    # add tags
    for blog_id, tag in query(tags_query):
        blogs[blog_id].tags.append(tag.decode('utf8'))

    return sorted(blogs.values(), key=lambda b: b.ctime)


def get_tagged_blogs(blogs):
    return [b for b in blogs if b.tags]


def get_music_blogs(blogs):
    return [b for b in blogs if '<div class="music">' in b.data]


def get_video_blogs(blogs):
    return [b for b in blogs if '<div class="video">' in b.data]


def get_migrated_blogs(blogs):
    return [b for b in blogs if b.source]


def translate_http_to_https(blog):
    lines = blog.data.split('\n')
    lines[0] = lines[0].replace('http', 'https')
    blog.data = '\n'.join(lines)


def purge():
    cypher('match (n) detach delete n')


def build_properties_str(properties):
    return u'{{{}}}'.format(u', '.join(
        u'{}: "{}"'.format(k, v) for k, v in properties.items()
    ))


if __name__ == '__main__':
    blogs = make_blogs()

    map(translate_http_to_https, get_music_blogs(blogs))
    map(translate_http_to_https, get_video_blogs(blogs))

    #blogs = blogs[:10]

    purge()

    blog_ids = []
    n = len(blogs)
    for i, blog in enumerate(blogs):
        params = {
            'content': blog.data,
            'ctime': blog.ctime,
            'mtime': blog.ctime,
            'id': i,
        }
        if blog.title:
            params['title'] = blog.title
        if blog.tags:
            params['tags'] = blog.tags
        properties_str = '{{{}}}'.format(', '.join(
            '{name}: {{{name}}}'.format(name=property_name)
            for property_name in params.keys()
        ))

        query = u'create (blog:Blog{}) return id(blog)'.format(properties_str)
        r = cypher(query, params)
        assert 'data' in r
        blog_ids.append(r['data'][0][0])
        print '{}/{} creating blogs'.format(i + 1, n)

    # linking blogs by now/prev relationship
    print
    for i, (now_id, prev_id) in enumerate(zip(blog_ids[:-1], blog_ids[1:])):
        print '{}/{} linking {} -> {}'.format(i + 1, n - 1, now_id, prev_id)
        r = cypher('''
            match (now), (prev) where id(now) = {} and id(prev) = {}
            create (now)-[:previous_blog]->(prev)
               '''.format(now_id, prev_id))
        assert 'data' in r
