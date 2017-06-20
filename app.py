import os
import json
import itertools
from datetime import datetime

import flask
from flask import request
from flask_cors import CORS

import session
import db
import user
import utils
import node
from node import Node
import config
from utils import (
    success_response, error_response,
    check,
    require_login, allow_public_access,
    strftime, strptime,
    Response,
)
from api import api, API
from paramtypes import String, Integer, Dict, List

build_dir = './frontend/build'

app = flask.Flask(__name__, static_folder=build_dir)
CORS(app)
API(app)

@app.route('/static/<path:path>')
def send_static(path):
    fpath = os.path.join(build_dir, 'static', path)
    dirname = os.path.dirname(fpath)
    fname = os.path.basename(fpath)
    print fpath
    return flask.send_from_directory(dirname, fname)

@app.route('/')
#@app.route('/<path:path>')
def index(path=''):
    return flask.send_from_directory(build_dir, 'index.html')

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

class ThisNode(object):

    pass

def node_from_id(node_id):
    if node_id == 0:
        return ThisNode()
    else:
        return Node(node_id)

def node_from_ref(ref):
    nodes = query(ref=ref)
    if not nodes:
        raise NotFound('no node with ref={}'.format(ref))
    elif len(nodes) == 1:
        return nodes[0]
    else:
        raise Response({
            'detail': 'multiple nodes with ref={} are found'.format(ref),
            'ids': [node.id for node in nodes]
        })

def node_from_literal(literal):
    node = Node(literal['data'])
    links = literal['links']
    for link in links:
        rel = link['rel']
        dst = link['dst']
        if isinstance(dst, ThisNode):
            dst = node
        node.link(rel, dst)
    return node

Link = Dict({})

NodeLiteral = Dict({
    'data': String,
    'links': List(Link, default=lambda: []),
}, coerce=node_from_literal)

Link.update({
    'rel': String,
    'dst': (
        String(coerce=node_from_ref)
        | Integer(coerce=node_from_id)
        | NodeLiteral
    ),
})

@api('POST', '/api/node', NodeLiteral,

    NodeLiteral={
        'data': String,
        'links': List(Link, default=lambda: []),
    },
    Link={
        'rel': String,
        'dst': (
            String(coerce=node_from_ref)
            | Integer(coerce=node_from_id)
            | NodeLiteral
        ),
    }
)
def post_node(node):
    node.graph.dump()
    return success_response({'node': dict(node)})

@app.route('/api/node/<int:node_id>', methods=['PUT'])
def put_node(node_id):
    new_node = request.json
    if not new_node:
        return error_response('invalid node: {}'.format(new_node))
    node = do_get_node_by_id(node_id)
    if not node:
        return error_response('not found', 404)
    #old_node = do_post_node(node['data'], ctime=node['ctime'])
    #if 'links' not in new_node:
    #    new_node['links'] = []
    do_update_node(node, new_node)
    #db.execute('insert into links (rel, src, dst) values (%s,%s,%s)',
    #           ('old', node['id'], old_node['id']))
    return success_response({'id': node_id})

@app.route('/api/node')
def get_nodes():
    nodes = node.query(options=request.args)
    return success_response({'nodes': map(dict, nodes)})

@app.route('/api/node/<int:node_id>')
def get_node_by_id(node_id):
    return success_response({'node': dict(Node(node_id))})

@app.route('/api/node/<ref>')
def get_node_by_ref(ref):
    node = node.query({'ref': ref})[0]
    return success_response({'node': node})

def do_get_node_by_id(node_id):
    r = db.queryone(
        'select data, ctime from nodes where id = %s',
        (node_id,)
    )
    if not r:
        return None
    data, ctime = r
    return {
        'id': node_id,
        'data': data,
        'ctime': strftime(ctime),
    }

def do_update_node(old_node, new_node):
    db.execute('update nodes set data = %s where id = %s', (
        new_node['data'].encode('utf8'), old_node['id'],
    ))

#@app.route('/api/node/<int:node_id>', methods=['DELETE'])
#def delete_node(node_id):
#    found = db.queryone('select 1 from nodes where id = %s', (node_id,))
#    if not found:
#        return error_response({'detail': 'not found', 'id': node_id}, 404)
#    db.execute('delete from nodes where id = %s', (node_id,))
#    return success_response({'id': node_id})

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
