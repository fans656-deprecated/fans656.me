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

def dbexecute(*sql):
    with getdb() as c:
        c.execute(*sql)

def dbquery(*sql):
    with getdb() as c:
        c.execute(*sql)
        r = c.fetchall()
        if r and len(r[0]) == 1:
            r = [t[0] for t in r]
        return r

def dbquery1(*sql):
    r = dbquery(*sql)
    return r[0] if r else None

def user_existed(username):
    r = dbquery1('select count(*) from users where username = ?', (username,))
    return r == 1

def init_db(purge=False):
    db = getdb()
    c = db.cursor()
    if purge:
        c.execute('drop table if exists users')
    c.execute('''
create table if not exists users (
    username varchar(255) unique,
    salt char(64),
    hashed_pwd char(64),
    iterations int
)
              ''')
    if purge:
        c.execute('drop table if exists sessions')
    c.execute('''
create table if not exists sessions (
    id char(64) unique,
    username varchar(255),
    ctime datetime,
    expires datetime
)
              ''')

if __name__ == '__main__':
    init_db()
    print 'database inited'
