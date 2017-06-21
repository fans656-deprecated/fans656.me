import os

import flask
from flask import request
from flask_cors import CORS

import node
from node import Node, get_node_by_id
import user
import session
import file_util
import utils
import config
from api import api, API
from utils import (
    success_response, error_response,
    check,
    strftime, strptime,
)
from errors import (
    NotFound, Existed, ServerError, NotAllowed, BadRequest,
    Conflict_409, InternalServerError_500, Forbidden_403, BadRequest_400,
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

############################################################# files

@app.route('/api/file/<path:fpath>', methods=['POST'])
def post_file(fpath):
    isdir = request.args.get('isdir')
    if isdir:
        return success_response()
    else:
        filesize = int(request.headers.get('Content-Length'))
        try:
            file_util.save(fpath, filesize)
            return success_response({
                'fpath': fpath,
                'size': filesize,
            })
        except Existed as e:
            return error_response(e.message, Conflict_409)
        except NotAllowed as e:
            return error_response(e.message, Forbidden_403)
        except ServerError as e:
            return error_response(e.message, InternalServerError_500)
        except BadRequest as e:
            return error_response(e.message, BadRequest_400)
        except Exception as e:
            return error_response(e.message)

@app.route('/file/<path:fpath>')
def get_file(fpath):
    user_fpath = fpath
    fpath = file_util.rooted_path(config.FILES_ROOT, fpath)
    if not fpath:
        return error_response({
            'detail': 'invalid path',
            'path': user_fpath,
        })
    if not os.path.exists(fpath):
        return error_response({
            'detail': 'not found',
            'path': user_fpath,
        }, 404)
    dirname = os.path.dirname(fpath)
    fname = os.path.basename(fpath)
    return flask.send_from_directory(dirname, fname)

@app.route('/api/file')
def list_root_file_directory():
    return success_response({
        'files': file_util.list_file_directory('')
    })

@app.route('/api/file/<path:dirpath>')
def list_file_directory(dirpath):
    return success_response({
        'files': file_util.list_file_directory(dirpath)
    })

############################################################# main

@app.route('/static/<path:path>')
def send_static(path):
    fpath = os.path.join(build_dir, 'static', path)
    dirname = os.path.dirname(fpath)
    fname = os.path.basename(fpath)
    return flask.send_from_directory(dirname, fname)

@app.route('/')
@app.route('/<path:path>')
def index(path=''):
    return flask.send_from_directory(build_dir, 'index.html')

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
    #from gevent.wsgi import WSGIServer
    #server = WSGIServer(('', 6561), app)
    #server.serve_forever()
    app.run(host='0.0.0.0', port=6561, debug=True)
