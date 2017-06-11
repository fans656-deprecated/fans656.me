import config
if config.db_engine == 'mysql':
    import pymysql as DB
    conn_params = {
        'host': 'localhost',
        'user': config.db_username,
        'passwd': config.db_password,
        'db': config.db_db,
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

def execute(*sql):
    with getdb() as c:
        c.execute(*sql)

def query(*sql):
    with getdb() as c:
        c.execute(*sql)
        r = c.fetchall()
        if r and len(r[0]) == 1:
            r = [t[0] for t in r]
        return r

def queryone(*sql):
    r = query(*sql)
    return r[0] if r else None

def init_db(purge=False):

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
    create_table('blogs', (
        'id serial,'
        'username varchar(255),'
        'content text,'
        'json text'
    ))
    create_table('blogs', (
        'id serial,'
        'username varchar(255),'
        'title text,'
        'content text,'
        'json text,'
        'visible_to varchar(255),'
        'ctime datetime,'
        'mtime datetime'
    ), purge=True)
    create_table('blog_tags', (
        'id serial,'
        'blog_id bigint,'
        'tag text'
    ))

if __name__ == '__main__':
    init_db()
    print 'database inited'
