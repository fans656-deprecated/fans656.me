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
    ok, error, notfound,
    check,
    require_login, allow_public_access,
    strftime, strptime,
)
from api import params, Int, String, Link

build_dir = './frontend/build'

app = flask.Flask(__name__, static_folder=build_dir)
CORS(app)

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
        return error('invalid data')
    try:
        user.login(username, password)
        resp = ok()
        resp.set_cookie('session', session.new_session(username))
        return resp
    except user.InvalidAuth as e:
        return error(e.message)

@app.route('/api/logout')
def get_logout():
    if session.del_session():
        return ok()
    else:
        return error('delete session failed')

@app.route('/api/me')
def get_me():
    return ok({'user': session.current_user()})

@app.route('/api/node', methods=['POST'])
@params({
    'data': String,
    'links': [Int | String | Link],
})
def post_node():
    node = request.json
    assert node, 'invalid node'

    node_data = node.get('data')
    if node_data is None:
        return error('node must have data')

    links = []
    for link in node.get('links', []):
        check(isinstance(link, dict),
              'link must have dict rel: {}'.format(link))

        rel = link.get('rel', None)
        assert rel, 'link must have rel: {}'.format(link)

        dst_recipe = link.get('dst', None)  # id / ref / node_literal
        #dst_node = Node(dst_recipe)
        if dst_recipe is None:
            return error('link must have dst: {}'.format(link))
        if isinstance(dst_recipe, (str, unicode)):
            ref = dst_recipe
            dst_node_id = node_ref_to_node_id(ref)
            if dst_node_id is None:
                return error('no node ref {}'.format(link))
        elif isinstance(dst_recipe, int):
            dst_node_id = dst_recipe
        elif isinstance(dst_recipe, dict):
            assert False, 'todo'
        else:
            return error('link dst must be ref or id: {}'.format(link))
        if dst_node_id > 0:
            try:
                found = db.queryone('select 1 from nodes where id = %s',
                                    dst_node_id)
                if not found:
                    return error('link dst node does not exist: {}'.format(
                        dst_node_id))
            except Exception:
                return error('invalid link dst: {}'.format(dst_node_id))

        links.append((rel, dst_node_id))

    return ok(do_post_node(node_data, links))

@app.route('/api/node/<int:node_id>', methods=['PUT'])
def put_node(node_id):
    new_node = request.json
    if not new_node:
        return error('invalid node: {}'.format(new_node))
    node = do_get_node_by_id(node_id)
    if not node:
        return error('not found', 404)
    #old_node = do_post_node(node['data'], ctime=node['ctime'])
    #if 'links' not in new_node:
    #    new_node['links'] = []
    do_update_node(node, new_node)
    #db.execute('insert into links (rel, src, dst) values (%s,%s,%s)',
    #           ('old', node['id'], old_node['id']))
    return ok({'id': node_id})

@app.route('/api/node')
def get_nodes():
    nodes = node.query(options=request.args)
    return ok({'nodes': map(dict, nodes)})

@app.route('/api/node/<int:node_id>')
@params({})
def get_node_by_id(node_id):
    return ok({'node': dict(Node(node_id))})

@app.route('/api/node/<ref>')
def get_node_by_ref(ref):
    node = node.query({'ref': ref})[0]
    return ok({'node': node})

def do_post_node(data, links=None, ctime=None):
    ctime = ctime or datetime.now()
    links = links or []
    db.execute('insert into nodes (data, ctime) values (%s,%s)',
               (data.encode('utf8'), ctime))
    node_id = db.queryone('select last_insert_id() from nodes')

    src_node_id = node_id
    link_ids = []
    for rel, dst_node_id in links:
        dst_node_id = dst_node_id or src_node_id
        db.execute('insert into links (rel, src, dst) values (%s,%s,%s)',
                   (rel.encode('utf8'), src_node_id, dst_node_id))
        link_ids.append(db.queryone('select last_insert_id() from links'))
    return {
        'id': node_id,
        'links': link_ids,
    }

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

def node_ref_to_node_id(ref):
    node_id = db.queryone('select n.id from nodes as n, links as l where '
                          'l.rel = "ref" and l.dst = n.id and n.data = %s',
                          (ref,))
    return node_id

#@app.route('/api/node/<int:node_id>', methods=['DELETE'])
#def delete_node(node_id):
#    found = db.queryone('select 1 from nodes where id = %s', (node_id,))
#    if not found:
#        return error({'detail': 'not found', 'id': node_id}, 404)
#    db.execute('delete from nodes where id = %s', (node_id,))
#    return ok({'id': node_id})

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
