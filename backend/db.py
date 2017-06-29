import os
import json
from datetime import datetime

import requests

import conf


def query(query, params=None):
    return cypher(query, params)


def query_one(query, params=None):
    r = cypher(query, params)
    print '=' * 70
    print 'query:', query
    print r
    print '=' * 70
    rows = r['data']
    row = rows[0]
    if len(row) == 1:
        return row[0]
    else:
        return row


def query_node(query, params=None):
    data = query_one(query, params)
    node = data['data']
    node.update({
        'id': data['metadata']['id'],
    })
    return node


def execute(query, params=None):
    return cypher(query, params)


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

if __name__ == '__main__':
    from pprint import pprint
    execute('''
create (u:User{
    username: 'fans656',
    password: '',
})
            ''')
