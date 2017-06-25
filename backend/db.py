import os
from datetime import datetime

import config
if config.db_engine == 'mysql':
    import pymysql as DB
    conn_params = {
        'host': 'localhost',
        'user': config.db_username,
        'passwd': config.db_password,
        'db': config.db_name,
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
        config.db_username,
        config.db_password,
        config.db_name,
    ))

def insert_meta_nodes():
    from node import Node
    blog = Node('blog')
    blog.link('ref', blog)
    blog.graph.dump()

def backup_db():
    fname = '{}-mysqldump-{}.sql'.format(
        datetime.now().strftime('%Y%m%d%H%M%S'),
        config.db_name,
    )
    print '*** Backuping database {} to {} ***'.format(
        config.db_name,
        fname,
    )
    os.system('mysqldump -u{} -p{} {} > {}'.format(
        config.db_username,
        config.db_password,
        config.db_name,
        fname,
    ))

if __name__ == '__main__':
    #init_db()
    #insert_meta_nodes()
    managedb()
