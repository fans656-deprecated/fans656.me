# coding: utf-8
import json
import urllib
import subprocess

from db import init_db

PREFIX = 'http://localhost:6561'

def post(url, data=None):
    data = data or {}
    headers = {'Content-Type': 'application/json'}
    headers = ["-H '{}:{}'".format(k, v) for k, v in headers.items()]
    args = "-X POST {headers} -d '{data}'".format(
        headers=' '.join(headers),
        data=json.dumps(data).replace("'", r"'\''"),
    )
    return curl(args, url)

def put(url, data=None):
    data = data or {}
    headers = {'Content-Type': 'application/json'}
    headers = ["-H '{}:{}'".format(k, v) for k, v in headers.items()]
    args = "-X PUT {headers} -d '{data}'".format(
        headers=' '.join(headers),
        data=json.dumps(data).replace("'", r"'\''"),
    )
    return curl(args, url)

def get(url, data=None):
    return curl('-G', url + encode_dict_as_url_args(data))

def delete(url, data=None):
    return curl('-X DELETE', url + encode_dict_as_url_args(data))

def encode_dict_as_url_args(data):
    if not data:
        return ''
    args = [(urllib.quote(k), urllib.quote(v)) for k, v in data.items()]
    return '&'.join('{}={}'.format(*kv) for kv in args)

def curl(args, url):
    url = 'http://localhost:6561' + url
    cmd = 'curl -s4 {args} "{url}"'.format(args=args, url=url)
    r = subprocess.check_output(cmd, shell=True)
    return json.loads(r)

def post_node(json_node):
    return post('/api/node', json_node)

def delete_node(node_id):
    return delete('/api/node/{}'.format(node_id))

def purge():
    init_db(quite=True)

if __name__ == '__main__':
    from pprint import pprint
    #purge()
    #pprint(post_node({
    #    'data': 'blog',
    #    'links': [
    #        {'rel': 'ref', 'dst': 0}
    #    ]
    #}))

    node = {
        'data': 'foo',
        'links': [
            {'rel': 'foo', 'dst': {'data': 'hi'}},
            {'rel': 'ref', 'dst': 0},
        ],
    }

    r = post_node(node)
    pprint(r)
