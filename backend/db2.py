import os
import json
from datetime import datetime

import requests

import config as conf


def query(query, params=None):
    return cypher(query, params)


def queryone(query, params=None):
    r = cypher(query, params)
    rows = r['data']
    cols = rows[0]
    data = cols[0]
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
    r = cypher('match (n) where id(n) = 935 return n')
    rows = r['data']
    cols = rows[0]
    data = cols[0]
    node = data['data']
    node.update({
        'id': data['metadata']['id'],
    })
    pprint(node)
