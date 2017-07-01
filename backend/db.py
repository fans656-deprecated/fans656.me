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


def query(query, params=None):
    return cypher(query, params)


def query_one(query, params=None):
    r = cypher(query, params)
    rows = r['data']
    if not rows:
        return None
    row = rows[0]
    if len(row) == 1:
        return row[0]
    else:
        return row


def query_nodes(q, params=None):
    data = query(q, params)
    rows = data['data']
    nodes = [row[0]['data'] for row in rows]
    return nodes


def query_node(query, params=None):
    data = query_one(query, params)
    if not data:
        return None
    node = data['data']
    return node


def execute(query, params=None):
    r = cypher(query, params)
    assert 'data' in r, str(r)
    return r


def cypher(query, params=None):
    data = {
        'query': query,
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
        self.node_id = metadata['id']
        self.properties = node['data']
        if 'id' not in self.properties:
            self.properties['id'] = self.node_id

    def __repr__(self):
        return unicode(self).encode('utf8')

    def __unicode__(self):
        return json.dumps({
            'node_id': self.node_id,
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

    def __init__(self, rel):
        metadata = rel['metadata']
        self.rel_id = metadata['id']
        self.type = rel['type']
        self.start_id = rel['start'].split('/')[-1]
        self.end_id = rel['end'].split('/')[-1]
        self.properties = rel['data']

    @property
    def create_statement(self):
        s = (
            u'match (start), (end) '
            u'where id(start) = {start_id} '
            u'and id(end) = {end_id} '
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
    r = query(q)
    rows = r['data']
    objs = [cls(row[0]) for row in rows]
    return objs

def gen_create_statements():
    nodes = make('match (n) return n', Node)
    rels = make('match ()-[r]->() return r', Relationship)
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
    nodes = query('''
match (n:Blog)
return id(n), n.ctime
               ''')['data']
    import util
    n = len(nodes)
    print n
    for i, (node_id, ctime) in enumerate(nodes):
        print '{}/{}'.format((i + 1), n)
        query('match (n) where id(n) = {node_id} set n.id = {id}', {
            'node_id': node_id,
            'id': util.id_from_ctime(ctime)
        })

def set_persisted_ids():
    nodes = query('match (n) return id(n)')['data']
    import util
    n = len(nodes)
    print n
    for i, (node_id,) in enumerate(nodes):
        print '{}/{}'.format((i + 1), n)
        r = query('match (n) where id(n) = {node_id} set n.id = {id}', {
            'node_id': node_id,
            'id': str(i + 1),
        })


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
    r = query_node('match (n:Session) return n')
    pprint(r)
