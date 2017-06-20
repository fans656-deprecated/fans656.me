import os

import flask
from flask import request
from flask_cors import CORS

import node
from node import Node, get_node_by_id
import user
import session
from api import api, API
from utils import (
    success_response, error_response,
    check,
    strftime, strptime,
    NotFound,
)
from paramtypes import (
    String, Integer, Dict, List,
    NodeLiteral, Link,
    node_from_ref, node_from_id, node_from_literal,
)

build_dir = './frontend/build'

app = flask.Flask(__name__, static_folder=build_dir)
CORS(app)
API(app)

############################################################# main

@app.route('/static/<path:path>')
def send_static(path):
    fpath = os.path.join(build_dir, 'static', path)
    dirname = os.path.dirname(fpath)
    fname = os.path.basename(fpath)
    print fpath
    return flask.send_from_directory(dirname, fname)

@app.route('/')
def index(path=''):
    return flask.send_from_directory(build_dir, 'index.html')

############################################################# user

@app.route('/api/login', methods=['POST'])
def post_login():
    try:
        username = flask.request.json.get('username', '').encode('utf8')
        password = flask.request.json.get('password', '').encode('utf8')
    except Exception:
        return error_response('invalid data')
    try:
        user.login(username, password)
        resp = success_response()
        resp.set_cookie('session', session.new_session(username))
        return resp
    except user.InvalidAuth as e:
        return error_response(e.message)

@app.route('/api/logout')
def get_logout():
    if session.del_session():
        return success_response()
    else:
        return error_response('delete session failed')

@app.route('/api/me')
def get_me():
    return success_response({'user': session.current_user()})

############################################################# node

@api('POST', '/api/node', NodeLiteral,

    example = {
        'data': 'this is the content',
        'links': [
            {'rel': 'type', 'dst': 'blog'},
            {'rel': 'title', 'dst': {'data': 'this is the title'}},
            {'rel': 'tag', 'dst': {'data': 'tag1'}},
            {'rel': 'tag', 'dst': {'data': 'tag2'}},
        ]
    },

    where_NodeLiteral = Dict({
        'data': String,
        'links': List(Link, default=lambda: []),
    }, coerce=node_from_literal),

    where_Link = Dict({
        'rel': String,
        'dst': (
            String(coerce=node_from_ref)
            | Integer(coerce=node_from_id)
            | NodeLiteral
        ),
    })
)
def post_node(node):
    print 'posting node'
    from pprint import pprint
    pprint(dict(node))
    node.graph.dump()
    return success_response({'node': dict(node)})

@api('PUT', '/api/node/<int:node_id>', NodeLiteral,

    example = {
        'data': 'this is the content',
        'links': [
            {'rel': 'type', 'dst': 'blog'},
            {'rel': 'title', 'dst': {'data': 'this is the title'}},
            {'rel': 'tag', 'dst': {'data': 'tag1'}},
            {'rel': 'tag', 'dst': {'data': 'tag2'}},
        ]
    },

    where_NodeLiteral = Dict({
        'data': String,
        'links': List(Link, default=lambda: []),
    }, coerce=node_from_literal),

    where_Link = Dict({
        'rel': String,
        'dst': (
            String(coerce=node_from_ref)
            | Integer(coerce=node_from_id)
            | NodeLiteral
        ),
    })
)
def put_node(node, node_id):
    node.id = node_id
    node.graph.dump()
    return success_response({'node': dict(node)})

@app.route('/api/node')
def get_nodes():
    """Get node list

    example:

        GET /api/node?type=blog&tag=foo&tag=bar
    """
    rels = {k: v[0] for k, v in dict(request.args).items()}
    print rels
    nodes = node.query(**rels)
    return success_response({'nodes': map(dict, nodes)})

@app.route('/api/node/<int:node_id>')
def api_get_node_by_id(node_id):
    try:
        node = get_node_by_id(node_id)
        return success_response({'node': dict(node)})
    except NotFound:
        return error_response({'detail': 'not found', 'ref': ref})

@app.route('/api/node/<ref>')
def get_node_by_ref(ref):
    try:
        node = node_from_ref(ref)
        return success_response({'node': dict(node)})
    except NotFound:
        return error_response({'detail': 'not found', 'ref': ref})

@app.route('/api/node/<int:node_id>', methods=['DELETE'])
def delete_node(node_id):
    return error_response('currently node delete is not supported')

############################################################# misc

#@app.route('/', subdomain='<subdomain>')
#def subdomain_dispatch(subdomain):
#    if user.exists(subdomain):
#        return '{}\'s space'.format(subdomain)
#    return 'subdomain: "{}"'.format(subdomain)

@app.after_request
def after_request(response):
    if 'Access-Control-Allow-Origin' not in response.headers:
        response.headers.add('Access-Control-Allow-Origin',
                             flask.request.headers.get('Origin', '*'))
    response.headers.add('Access-Control-Allow-Headers',
                         'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods',
                         'GET,PUT,POST,DELETE,OPTIONS')
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    return response

@app.teardown_appcontext
def close_db(err):
    if hasattr(flask.g, 'db'):
        flask.g.db.close()

@app.context_processor
def override_url_for():
    def f_(endpoint, **values):
        if endpoint == 'static':
            filename = values.get('filename', None)
            if filename:
                file_path = os.path.join(app.root_path,
                                         endpoint, filename)
                values['q'] = int(os.stat(file_path).st_mtime)
        return flask.url_for(endpoint, **values)
    return dict(url_for=f_)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=6561, threaded=True, debug=True)
