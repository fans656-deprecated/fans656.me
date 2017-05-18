try:
    from pysqlite2 import dbapi2 as DB
except ImportError:
    import sqlite3 as DB

conn_params = {
    'database': 'all.db',
}

def connect_db():
    return DB.connect(**conn_params)

if __name__ == '__main__':
    db = connect_db()
    c = db.cursor()
    c.execute('drop table if exists users')
    c.execute('''
create table users (
    username varchar(255),
    salted_pwd char(20),
    salt char(16)
)
              ''')
