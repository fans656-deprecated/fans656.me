#!/usr/bin/env python
import os
import sys
import json
import itertools
import subprocess
from datetime import datetime

import requests
from f6 import each

import conf


def query(stmt, params=None, rows=None, cols=None, one=False,
          relationship=False):
    if one:
        rows = cols = 1

    if relationship:
        _extract_node = lambda x: x
    else:
        _extract_node = extract_node
    extract = lambda row: map(_extract_node, row) if row else None
    r = cypher(stmt, params)
    assert 'data' in r, str(r)
    data_rows = r['data']
    if not data_rows:
        return []
    if rows == 1:
        data_rows = data_rows[:1]
    res = [extract(row) for row in data_rows]
    if cols == 1:
        res = [t[0] for t in res]
    return res[0] if rows == 1 else res


def pquery(stmt, params=None, pause=False, rows=None, cols=None, one=False):
    pprint(query(stmt, params, rows, cols, one=one))


def execute(stmt, params=None):
    r = cypher(stmt, params)
    assert 'data' in r, str(r)
    return r


def cypher(stmt, params=None):
    data = {
        'query': stmt,
        'params': params or {},
    }
    r = requests.post(
        conf.neo4j_db,
        auth=(conf.neo4j_user, conf.neo4j_password),
        headers={'Content-Type': 'application/json'},
        data=json.dumps(data),
    )
    return json.loads(r.text)

class Node(object):

    def __init__(self, node):
        metadata = node['metadata']
        self.labels = metadata['labels']
        self.properties = node['data']
        if 'id' not in self.properties:
            self.properties['id'] = self.node_id

    def __repr__(self):
        return unicode(self).encode('utf8')

    def __unicode__(self):
        return json.dumps({
            'labels': self.labels,
            'properties': self.properties
        })

    @property
    def create_statement(self):
        return u'create ({labels}{properties})'.format(
            labels=''.join(':{}'.format(label) for label in self.labels),
            properties=make_properties_str(self.properties),
        )

class Relationship(object):

    def __init__(self, rel, start_id, end_id):
        self.rel = rel
        self.type = rel['type']
        self.start_id = start_id
        self.end_id = end_id
        self.properties = rel['data']

    @property
    def create_statement(self):
        s = (
            u'match (start), (end) '
            u'where start.id = "{start_id}" and end.id = "{end_id}" '
            u'create (start)-[:{type}{properties}]->(end) '
        )
        return s.format(
            type=self.type,
            start_id=self.start_id,
            end_id=self.end_id,
            properties=make_properties_str(self.properties),
        )

def make_properties_str(props):
    if not props:
        return ''
    else:
        return u'{{{}}}'.format(u', '.join(
            u'{}: {}'.format(k, create_repr(v))
            for k, v in props.items()))

def create_repr(value):
    if isinstance(value, list):
        return u'[{}]'.format(u', '.join(create_repr(t) for t in value))
    elif isinstance(value, (str, unicode)):
        return u'"{}"'.format(value.replace('"', r'\"'))
    else:
        return unicode(value)

def make(q, cls):
    r = cypher(q)
    rows = r['data']
    objs = [cls(row[0]) for row in rows]
    return objs

def gen_create_statements():
    nodes = make('match (n) return n', Node)

    r = query('match (start)-[rel]->(end) return rel, start.id, end.id',
              relationship=True)
    rels = [Relationship(rel, start_id, end_id)
            for rel, start_id, end_id in r]

    stmts = itertools.chain(each(nodes).create_statement,
                            each(rels).create_statement)
    return list(stmts)


def backup():
    backup_neo4j()
    backup_files()
    git_commit_and_push()
    #print 'backuped but not sync in cloud, you need to uncomment git push in db.py'


def restore():
    restore_neo4j()
    restore_files()


def backup_neo4j():
    root = conf.BACKUP_REPO_DIR
    if not os.path.exists(root):
        os.makedirs(root)

    dump_fpath = os.path.join(conf.BACKUP_REPO_DIR, conf.BACKUP_DUMP_FNAME)
    with open(dump_fpath, 'w') as f:
        json.dump({
            'statements': gen_create_statements(),
        }, f, indent=2)


def restore_neo4j():
    dump_fpath = os.path.join(conf.BACKUP_REPO_DIR, conf.BACKUP_DUMP_FNAME)
    with open(dump_fpath) as f:
        stmts = json.load(f)['statements']
    purge()
    n = len(stmts)
    for i, stmt in enumerate(stmts):
        r = execute(stmt)
        if 'data' not in r:
            print stmt
            assert False
        print '{}/{}'.format(i + 1, n)


def shell_execute(cmd, replacecmd=None):
    print
    print replacecmd or cmd
    if os.system(cmd):
        print 'ERROR! backup failed'
        exit(1)


def backup_files():
    root = conf.BACKUP_REPO_DIR

    if not os.path.exists(root):
        os.makedirs(root)

    backup_repo_dir = conf.BACKUP_REPO_DIR
    backup_file_dir = os.path.join(backup_repo_dir, 'files')
    local_file_dir = conf.FILES_ROOT

    # rsync files
    shell_execute('rsync -av {} {}'.format(local_file_dir + '/',
                                     backup_file_dir + '/'))


def restore_files():
    backup_repo_dir = conf.BACKUP_REPO_DIR
    backup_file_dir = os.path.join(backup_repo_dir, 'files')
    local_file_dir = conf.FILES_ROOT

    shell_execute('rsync -av {}/ {}'.format(backup_file_dir, local_file_dir))

    print
    print
    print '*' * 70
    print 'OK! Data restored at {}'.format(datetime.now())


def git_commit_and_push():
    os.chdir(conf.BACKUP_REPO_DIR)
    shell_execute('pwd')
    if not os.path.exists('.git'):
        shell_execute('git init')
    if not subprocess.check_output('git remote -v', shell=True):
        shell_execute('git remote add origin {}'.format(conf.DATA_REMOTE_REPO))

    shell_execute('git add --all')
    shell_execute('git commit -m "{}"'.format(
        datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    ))
    shell_execute('git push origin master')

    print 'backed up at {}'.format(datetime.now())


def purge():
    cypher('match (n) detach delete n')


def set_persisted_ids():
    nodes = cypher('''
match (n:Blog)
return id(n), n.ctime
               ''')['data']
    import util
    n = len(nodes)
    print n
    for i, (node_id, ctime) in enumerate(nodes):
        print '{}/{}'.format((i + 1), n)
        cypher('match (n) where id(n) = {node_id} set n.id = {id}', {
            'node_id': node_id,
            'id': util.id_from_ctime(ctime)
        })

def set_persisted_ids():
    nodes = cypher('match (n) return id(n)')['data']
    import util
    n = len(nodes)
    print n
    for i, (node_id,) in enumerate(nodes):
        print '{}/{}'.format((i + 1), n)
        r = cypher('match (n) where id(n) = {node_id} set n.id = {id}', {
            'node_id': node_id,
            'id': str(i + 1),
        })


def extract_node(row):
    if isinstance(row, dict) and 'metadata' in row:
        r =  row['data']
        r['meta'] = {
            'labels': row['metadata']['labels'],
        }
        return r
    else:
        return row


if __name__ == '__main__':
    import sys
    from pprint import pprint

    if len(sys.argv) == 2:
        if sys.argv[1] == '-b':
            backup()
            exit()
        elif sys.argv[1] == '-r':
            restore()
            exit()

    #set_persisted_ids()
    r = query('match (n:User) return n')
    pprint(r)
